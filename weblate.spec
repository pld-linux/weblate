Summary:	Web-based translation tool
Name:		weblate
Version:	2.6
Release:	0.1
License:	GPL-3.0+
Group:		Applications/WWW
Source0:	http://dl.cihar.com/weblate/Weblate-%{version}.tar.xz
# Source0-md5:	03a94a59a940a5106469cf6501b9a886
#Source1:	Weblate-test-%{version}.tar.xz
URL:		https://weblate.org/
BuildRequires:	bitstream-vera
BuildRequires:	git
BuildRequires:	graphviz
BuildRequires:	graphviz-gd
BuildRequires:	mercurial
BuildRequires:	python-Babel
BuildRequires:	python-Django >= 1.7
BuildRequires:	python-Pillow
BuildRequires:	python-Sphinx
BuildRequires:	python-alabaster
BuildRequires:	python-dateutil
BuildRequires:	python-django-crispy-forms >= 1.4.0
BuildRequires:	python-django_compressor
BuildRequires:	python-djangorestframework
BuildRequires:	python-httpretty
BuildRequires:	python-python-social-auth >= 0.2
BuildRequires:	python-selenium
BuildRequires:	python-sphinxcontrib-httpdomain
BuildRequires:	python-whoosh >= 2.5.2
BuildRequires:	translate-toolkit >= 1.11.0
Requires:	apache2-mod_wsgi
Requires:	cron
Requires:	git
Requires:	python-Babel
Requires:	python-Django >= 1.7
Requires:	python-Pillow
Requires:	python-dateutil
Requires:	python-django-crispy-forms >= 1.4.0
Requires:	python-django_compressor
Requires:	python-djangorestframework
Requires:	python-python-social-auth >= 0.2
Requires:	python-whoosh >= 2.5.2
Requires:	translate-toolkit >= 1.11.0
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

%prep
%setup -q -n Weblate-%{version}

%if 0
# Extract test data
mkdir data-test
cd data-test
tar xvf %{SOURCE1}
mv Weblate-test-%{version}/* .
cd ..
%endif

%build
%{__make} -C docs html
# Copy example settings
cp weblate/settings_example.py weblate/settings.py
# Set correct directories in settings
sed -i 's@^BASE_DIR = .*@BASE_DIR = "%{WLDIR}/weblate"@g' weblate/settings.py
sed -i 's@^DATA_DIR = .*@DATA_DIR = "%{WLDATADIR}"@g' weblate/settings.py
sed -i "s@%{_datadir}/weblate/data@%{WLDATADIR}@" examples/apache.conf

%if %{with tests}
export LANG=en_US.UTF-8
# Collect static files for testsuite
./manage.py collectstatic --noinput --settings=weblate.settings_test -v 2
# Run the testsuite
./manage.py test --settings=weblate.settings_test -v 2
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/%{WLDIR}
install -d $RPM_BUILD_ROOT/%{WLETCDIR}

# Copy all files
cp -a . $RPM_BUILD_ROOT/%{WLDIR}
# Remove test data
rm -rf $RPM_BUILD_ROOT/%{WLDIR}/data-test

# We ship this separately
rm -rf $RPM_BUILD_ROOT/%{WLDIR}/docs
rm -f $RPM_BUILD_ROOT/%{WLDIR}/README.rst \
    $RPM_BUILD_ROOT/%{WLDIR}/ChangeLog \
    $RPM_BUILD_ROOT/%{WLDIR}/COPYING \
    $RPM_BUILD_ROOT/%{WLDIR}/INSTALL

# Byte compile python files
%py_compile $RPM_BUILD_ROOT/%{WLDIR}

# Move configuration to etc
mv $RPM_BUILD_ROOT/%{WLDIR}/weblate/settings.py $RPM_BUILD_ROOT/%{WLETCDIR}/
ln -s %{WLETCDIR}/settings.py $RPM_BUILD_ROOT/%{WLDIR}/weblate/settings.py

# Apache config
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/apache2/vhosts.d/
cp -p examples/apache.conf $RPM_BUILD_ROOT/%{_sysconfdir}/apache2/vhosts.d/weblate.conf

# Whoosh index dir
install -d $RPM_BUILD_ROOT/%{WLDATADIR}

%post
# Static files
%{WLDIR}/manage.py collectstatic --noinput

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc docs/_build/html
%doc README.rst
%config(noreplace) %{_sysconfdir}/weblate
%config(noreplace) %{_sysconfdir}/apache2
%{WLDIR}
%attr(755,wwwrun,www) %{WLDATADIR}
