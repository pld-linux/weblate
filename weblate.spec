#
# Conditional build:
%bcond_with	doc	# don't build doc
%bcond_with	tests	# do not perform "make test" (some tests require network)

%define		module		weblate
%define		egg_name	Weblate
Summary:	Web-based translation tool
Name:		weblate
Version:	2.13.1
Release:	0.4
License:	GPL v3.0+
Group:		Applications/WWW
Source0:	http://dl.cihar.com/weblate/Weblate-%{version}.tar.xz
# Source0-md5:	b6e3bd63f2cd63613410ec2dc925a96e
%if %{with tests}
Source1:	http://dl.cihar.com/weblate/Weblate-test-%{version}.tar.xz
# Source1-md5:	d3ae337b1808e7cd2c8a8ba53caa4ab1
%endif
URL:		https://weblate.org/
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(find_lang) >= 1.40
BuildRequires:	rpmbuild(macros) >= 1.714
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%if %{with doc}
BuildRequires:	fonts-TTF-bitstream-vera
BuildRequires:	python-sphinxcontrib.httpdomain
BuildRequires:	sphinx-pdg-2
%endif
%if %{with tests}
BuildRequires:	git-core
BuildRequires:	graphviz
BuildRequires:	graphviz-gd
BuildRequires:	mercurial
BuildRequires:	python-alabaster
BuildRequires:	python-babel
BuildRequires:	python-dateutil
BuildRequires:	python-defusedxml >= 0.4
BuildRequires:	python-django >= 1.10
BuildRequires:	python-django-appconf >= 1.0
BuildRequires:	python-django-compressor >= 2.1.1
BuildRequires:	python-django-crispy-forms >= 1.6.1
BuildRequires:	python-django-rest-framework >= 3.4
BuildRequires:	python-httpretty
BuildRequires:	python-pillow
BuildRequires:	python-selenium
BuildRequires:	python-siphashc3
BuildRequires:	python-social-auth-app-django >= 1.1.0
BuildRequires:	python-social-auth-core >= 1.2.0
BuildRequires:	python-tesserocr >= 2.0.0
BuildRequires:	python-whoosh >= 2.7.0
BuildRequires:	translate-toolkit >= 2.0.0
%endif
Requires:	apache-mod_wsgi-py2
Requires:	crondaemon
Requires:	python-babel
Suggests:	git-core
Suggests:	git-core-svn >= 2.10.0
Suggests:	python-MySQL-python
Suggests:	python-psycopg2
Suggests:	python-pyuca
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define WLDIR %{_datadir}/%{name}
%define WLDATADIR %{_localstatedir}/lib/%{name}
%define WLETCDIR %{_sysconfdir}/%{name}

%description
Weblate is a free web-based translation tool with tight version
control integration. It features simple and clean user interface,
propagation of translations across components, quality checks and
automatic linking to source files.

List of features includes:
- Easy web based translation
- Propagation of translations across components (for different
  branches)
- Tight git integration - every change is represented by Git commit
- Usage of Django's admin interface
- Upload and automatic merging of po files
- Links to source files for context
- Allows to use machine translation services
- Message quality checks
- Tunable access control
- Wide range of supported translation formats (Getext, Qt, Java,
  Windows, Symbian and more)

%package doc
Summary:	Manual for Weblate
Group:		Documentation

%description doc
Documentation for Weblate.

%prep
%setup -q -n Weblate-%{version} %{?with_tests:-a1}
%if %{with tests}
mv Weblate-test-%{version} data-test
%endif

# Copy example settings
cp -p weblate/settings_example.py weblate/settings.py
# Set correct directories in settings
sed -i 's@^BASE_DIR = .*@BASE_DIR = "%{WLDIR}/weblate"@g' weblate/settings.py
sed -i 's@^DATA_DIR = .*@DATA_DIR = "%{WLDATADIR}"@g' weblate/settings.py
sed -i "s@%{_datadir}/weblate/data@%{WLDATADIR}@" examples/apache.conf

%build
%py_build

%if %{with doc}
%{__make} -C docs html
%endif

%if %{with tests}
export LANG=en_US.UTF-8
# Collect static files for testsuite
./manage.py collectstatic --noinput --settings=weblate.settings_test -v 2
# Run the testsuite
./manage.py test --settings=weblate.settings_test -v 2
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{WLETCDIR},%{WLDIR},%{WLDATADIR}}

%py_install

# don't package tests
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/api/tests.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/billing/tests.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/gitexport/tests.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/lang/tests.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/permissions/tests.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/screenshots/tests.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/settings_test*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/test_*.py*
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/utils/unittest.py*
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/accounts/tests
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/billing/test-data
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/trans/tests
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/utils/tests

# move static content to fixed path for simplier webserver configs
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/%{module}/static,%{WLDIR}}
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/%{module}/templates,%{WLDIR}}
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/%{module}/ttf,%{WLDIR}}
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/%{module}/wsgi.py,%{WLDIR}}

# Move configuration to etc
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/%{module}/settings.py,%{WLETCDIR}}
ln -s %{WLETCDIR}/settings.py $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/settings.py

# Apache config
install -d $RPM_BUILD_ROOT%{_sysconfdir}/apache2/vhosts.d/
cp -p examples/apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache2/vhosts.d/weblate.conf

%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/locale/*.pot
%{__rm} $RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}/locale/*/LC_MESSAGES/*.po
%find_lang %{name} --with-django

%post
# Static files
%{WLDIR}/manage.py collectstatic --noinput

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README.rst
%config(noreplace) %{_sysconfdir}/weblate
%config(noreplace) %{_sysconfdir}/apache2
%attr(755,root,root) %{_bindir}/weblate
%{WLDIR}
%attr(755,wwwrun,www) %{WLDATADIR}
%dir %{py_sitescriptdir}/%{module}
%{py_sitescriptdir}/%{module}/*.py*
%{py_sitescriptdir}/%{module}/accounts
%{py_sitescriptdir}/%{module}/api
%{py_sitescriptdir}/%{module}/billing
%{py_sitescriptdir}/%{module}/gitexport
%{py_sitescriptdir}/%{module}/lang
%{py_sitescriptdir}/%{module}/permissions
%{py_sitescriptdir}/%{module}/screenshots
%{py_sitescriptdir}/%{module}/trans
%{py_sitescriptdir}/%{module}/utils
%dir %{py_sitescriptdir}/%{module}/locale
%{py_sitescriptdir}/%{egg_name}-%{version}-py*.egg-info

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif
