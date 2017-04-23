#
# Conditional build:
%bcond_with	doc	# don't build doc
%bcond_with	tests	# do not perform "make test" (some tests require network)

Summary:	Web-based translation tool
Name:		weblate
Version:	2.13.1
Release:	0.1
License:	GPL v3.0+
Group:		Applications/WWW
Source0:	http://dl.cihar.com/weblate/Weblate-%{version}.tar.xz
# Source0-md5:	b6e3bd63f2cd63613410ec2dc925a96e
%if %{with tests}
Source1:	http://dl.cihar.com/weblate/Weblate-test-%{version}.tar.xz
# Source1-md5:	d3ae337b1808e7cd2c8a8ba53caa4ab1
%endif
URL:		https://weblate.org/
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
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires:	apache2-mod_wsgi
Requires:	crondaemon
Requires:	python-babel
Requires:	python-dateutil
Requires:	python-defusedxml >= 0.4
Requires:	python-django >= 1.9
Requires:	python-django-compressor >= 2.1.1
Requires:	python-django-crispy-forms >= 1.6.1
Requires:	python-django-rest-framework >= 3.4
Requires:	python-pillow
Requires:	python-social-auth-app-django >= 1.1.0
Requires:	python-social-auth-core >= 1.2.0
Requires:	python-whoosh >= 2.5.2
Requires:	translate-toolkit >= 1.11.0
Suggests:	git-core
Suggests:	git-core-svn >= 2.10.0
Suggests:	python-MySQL-python
Suggests:	python-psycopg2
Suggests:	python-pyuca
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define WLDIR %{_datadir}/weblate
%define WLDATADIR %{_localstatedir}/lib/weblate
%define WLETCDIR %{_sysconfdir}/weblate

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
install -d $RPM_BUILD_ROOT%{WLDIR}
install -d $RPM_BUILD_ROOT%{WLETCDIR}

# Copy all files
cp -a . $RPM_BUILD_ROOT%{WLDIR}
# Remove test data
rm -rf $RPM_BUILD_ROOT%{WLDIR}/data-test

# We ship this separately
rm -rf $RPM_BUILD_ROOT%{WLDIR}/docs
rm -f $RPM_BUILD_ROOT%{WLDIR}/README.rst \
    $RPM_BUILD_ROOT%{WLDIR}/ChangeLog \
    $RPM_BUILD_ROOT%{WLDIR}/COPYING \
    $RPM_BUILD_ROOT%{WLDIR}/INSTALL

# Byte compile python files
%py_compile $RPM_BUILD_ROOT%{WLDIR}

# Move configuration to etc
mv $RPM_BUILD_ROOT%{WLDIR}/weblate/settings.py $RPM_BUILD_ROOT/%{WLETCDIR}/
ln -s %{WLETCDIR}/settings.py $RPM_BUILD_ROOT%{WLDIR}/weblate/settings.py

# Apache config
install -d $RPM_BUILD_ROOT%{_sysconfdir}/apache2/vhosts.d/
cp -p examples/apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache2/vhosts.d/weblate.conf

# Whoosh index dir
install -d $RPM_BUILD_ROOT%{WLDATADIR}

%post
# Static files
%{WLDIR}/manage.py collectstatic --noinput

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.rst
%config(noreplace) %{_sysconfdir}/weblate
%config(noreplace) %{_sysconfdir}/apache2
%{WLDIR}
%attr(755,wwwrun,www) %{WLDATADIR}

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif
