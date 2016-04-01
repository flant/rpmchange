%global sphinx_user sphinx
%global sphinx_group sphinx
%global sphinx_home %{_localstatedir}/lib/sphinx

# rpmbuild < 4.6 support
%if ! 0%{?__isa_bits}
%ifarch x86_64 ia64 ppc64 sparc64 s390x alpha ppc64le aarch64
%global __isa_bits 64
%else
%global __isa_bits 32
%endif
%endif

Name:		sphinx
Version:	2.2.10
Release:	2%{?dist}
Summary:	Free open-source SQL full-text search engine
License:	GPLv2+
URL:		http://sphinxsearch.com

Source0:	http://sphinxsearch.com/files/%{name}-%{version}-release.tar.gz
Source1:	searchd.service
Patch0:		%{name}-2.0.3-fix_static.patch
Patch1:		%{name}-2.0.3-default_listen.patch

BuildRequires:	expat-devel
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	systemd

Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd

# Users and groups
Requires(pre):		shadow-utils
       

%description
Sphinx is a full-text search engine, distributed under GPL version 2.
Commercial licensing (e.g. for embedded use) is also available upon request.

Generally, it's a standalone search engine, meant to provide fast,
size-efficient and relevant full-text search functions to other
applications. Sphinx was specially designed to integrate well with SQL
databases and scripting languages.

Currently built-in data source drivers support fetching data either via
direct connection to MySQL, or PostgreSQL, or from a pipe in a custom XML
format. Adding new drivers (e.g. native support other DBMSes) is
designed to be as easy as possible.

Search API native ported to PHP, Python, Perl, Ruby, Java, and also
available as a plug-gable MySQL storage engine. API is very lightweight so
porting it to new language is known to take a few hours.

As for the name, Sphinx is an acronym which is officially decoded as SQL
Phrase Index. Yes, I know about CMU's Sphinx project.


%package -n libsphinxclient
Summary:	Pure C search-d client API library


%description -n libsphinxclient
Pure C search-d client API library
Sphinx search engine, http://sphinxsearch.com/


%package -n libsphinxclient-devel
Summary:	Development libraries and header files for libsphinxclient
Requires:	libsphinxclient = %{version}-%{release}


%description -n libsphinxclient-devel
Pure C search-d client API library
Sphinx search engine, http://sphinxsearch.com/


%package java
Summary:		Java API for Sphinx
BuildRequires:	java-devel
Requires:		java-headless
Requires:		jpackage-utils


%description java
This package provides the Java API for Sphinx,
the free, open-source full-text search engine,
designed with indexing database content in mind.


%package php
Summary:	PHP API for Sphinx
Requires:	php-common >= 5.1.6


%description php
This package provides the PHP API for Sphinx,
the free, open-source full-text search engine,
designed with indexing database content in mind.


%prep
%setup -qn %{name}-%{version}-release
%patch0 -p1 -b .fix_static
%patch1 -p1 -b .default_listen

# Fix wrong-file-end-of-line-encoding
for f in \
	api/java/mk.cmd \
	api/ruby/test.rb \
	api/ruby/spec/sphinx/sphinx_test.sql \
	api/ruby/spec/sphinx/sphinx_test.sql \
; do
	sed -i 's/\r$//' ${f};
done

# Fix file not UTF8
iconv -f iso8859-1 -t utf-8 doc/sphinx.txt > doc/sphinx.txt.conv && mv -f doc/sphinx.txt.conv doc/sphinx.txt

%build
%if %{__isa_bits} == 64
%configure --sysconfdir=%{_sysconfdir}/sphinx --with-mysql --with-pgsql --enable-id64
%else
%configure --sysconfdir=%{_sysconfdir}/sphinx --with-mysql --with-pgsql
%endif

make %{?_smp_mflags}

# Build libsphinxclient
pushd api/libsphinxclient
    %configure
    make #%{?_smp_mflags}
popd


# make the java api
make -C api/java 


%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p -c"

install -p -D -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/searchd.service

# Create /var/log/sphinx
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/sphinx

# Create /var/run/sphinx
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/sphinx

# Create /var/lib/sphinx
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/sphinx

# Create sphinx.conf
cp $RPM_BUILD_ROOT%{_sysconfdir}/sphinx/sphinx-min.conf.dist \
    $RPM_BUILD_ROOT%{_sysconfdir}/sphinx/sphinx.conf
    
# Modify sphinx.conf
sed -i 's|/var/log/searchd.log|%{_localstatedir}/log/sphinx/searchd.log|g' \
    $RPM_BUILD_ROOT%{_sysconfdir}/sphinx/sphinx.conf

sed -i 's|/var/log/query.log|%{_localstatedir}/log/sphinx/query.log|g' \
    $RPM_BUILD_ROOT%{_sysconfdir}/sphinx/sphinx.conf

sed -i 's|/var/log/searchd.pid|%{_localstatedir}/run/sphinx/searchd.pid|g' \
    $RPM_BUILD_ROOT%{_sysconfdir}/sphinx/sphinx.conf

sed -i 's|/var/data|%{_localstatedir}/lib/sphinx|g' \
    $RPM_BUILD_ROOT%{_sysconfdir}/sphinx/sphinx.conf

# Create /etc/logrotate.d/sphinx
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/sphinx << EOF
%{_localstatedir}/log/sphinx/*.log {
       weekly
       rotate 10
       copytruncate
       delaycompress
       compress
       notifempty
       missingok
}
EOF

# Create /etc/logrotate.d/sphinx
mkdir -p $RPM_BUILD_ROOT%{_tmpfilesdir}
cat > $RPM_BUILD_ROOT%{_tmpfilesdir}/%{name}.conf << EOF
d %{_localstatedir}/run/sphinx 755 sphinx root -
EOF

# Install libsphinxclient
pushd api/libsphinxclient/
    make install DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p -c"
popd

# install the java api
mkdir -p $RPM_BUILD_ROOT%{_javadir}
install -m 0644 api/java/%{name}api.jar \
    $RPM_BUILD_ROOT%{_javadir}/%{name}.jar
ln -s %{_javadir}/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}api.jar

# install the php api
# "Non-PEAR PHP extensions should put their Class files in /usr/share/php."
# - http://fedoraproject.org/wiki/Packaging:PHP
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/php
install -m 0644 api/%{name}api.php $RPM_BUILD_ROOT%{_datadir}/php

# clean-up .la archives
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# clean-up .a archives
find $RPM_BUILD_ROOT -name '*.a' -exec rm -f {} ';'


%pre
getent group %{sphinx_group} >/dev/null || groupadd -r %{sphinx_group}
getent passwd %{sphinx_user} >/dev/null || \
useradd -r -g %{sphinx_group} -d %{sphinx_home} -s /bin/bash \
-c "Sphinx Search" %{sphinx_user}
exit 0

%post
%systemd_post searchd.service

%preun
%systemd_preun searchd.service

%post -n libsphinxclient -p /sbin/ldconfig

%postun -n libsphinxclient -p /sbin/ldconfig

%postun
%systemd_postun_with_restart searchd.service

%posttrans
chown -R %{sphinx_user}:root %{_localstatedir}/log/sphinx/
chown -R %{sphinx_user}:root %{_localstatedir}/run/sphinx/
chown -R %{sphinx_user}:root %{_localstatedir}/lib/sphinx/

%triggerun -- sphinx < 2.0.3-1
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save searchd >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del searchd >/dev/null 2>&1 || :
/bin/systemctl try-restart searchd.service >/dev/null 2>&1 || :


%files
%doc COPYING doc/sphinx.txt sphinx-min.conf.dist sphinx.conf.dist example.sql
%dir %{_sysconfdir}/sphinx
%config(noreplace) %{_sysconfdir}/sphinx/sphinx.conf
%exclude %{_sysconfdir}/sphinx/*.conf.dist
%exclude %{_sysconfdir}/sphinx/example.sql
%{_unitdir}/searchd.service
%config(noreplace) %{_sysconfdir}/logrotate.d/sphinx
%{_tmpfilesdir}/%{name}.conf
%{_bindir}/*
%dir %attr(0755, %{sphinx_user}, root) %{_localstatedir}/log/sphinx
%dir %attr(0755, %{sphinx_user}, root) %{_localstatedir}/run/sphinx
%dir %attr(0755, %{sphinx_user}, root) %{_localstatedir}/lib/sphinx
%{_mandir}/man1/*

%files -n libsphinxclient
%doc COPYING api/java api/ruby api/*.php api/*.py api/libsphinxclient/README
%{_libdir}/libsphinxclient-0*.so

%files -n libsphinxclient-devel
%{_libdir}/libsphinxclient.so
%{_includedir}/*

%files java
%doc api/java/README COPYING
%{_javadir}/*

%files php
%doc COPYING
%{_datadir}/php/*

%changelog
* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Sep 6 2015 Gerald Cox <gbcox@fedoraproject.org> - 2.2.10-1
- Upstream 2.2.10 rhbz#1260452

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Apr 20 2015 Gerald Cox <gbcox@fedoraproject.org> - 2.2.9-1
- Upstream 2.2.9 rhbz#1201311

* Sun Mar 29 2015 Gerald Cox <gbcox@fedoraproject.org> - 2.2.8-1
- Upstream 2.2.8 rhbz#1201311

* Wed Jan 21 2015 Gerald Cox <gbcox@fedoraproject.org> - 2.2.7-1
- Upstream 2.2.7

* Sat Nov 15 2014 Gerald Cox <gbcox@fedoraproject.org> - 2.2.6-1
- Upstream 2.2.6

* Mon Nov 10 2014 Peter Robinson <pbrobinson@fedoraproject.org> 2.2.5-2
- Drop ExclusiveArch as armv7hl issue is fixed and aarch64/ppc64/s390 never had issues

* Tue Oct 28 2014 Gerald Cox <gbcox@fedoraproject.org> - 2.2.5-1
- Upstream 2.2.5
- ExclusiveArch: %%{ix86} x86_64 rhbz#1107361

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 25 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.1.5-2
- Move to java-headless
- Resolves: rhbz#1068545

* Tue Mar 25 2014 Michael Simacek <msimacek@redhat.com> - 2.1.5-2
- Remove version from JAR name

* Sun Jan 26 2014 Peter Robinson <pbrobinson@fedoraproject.org> 2.1.5-1
- upstream 2.1.5

* Sun Jan 26 2014 Peter Robinson <pbrobinson@fedoraproject.org> 2.1.2-2
- Fix build with systemd
- Cleanup and modernise spec

* Sat Nov  2 2013 Christof Damian <christof@damian.net> - 2.1.2-1
- upstream 2.1.2

* Fri Jul 26 2013 Christof Damian <christof@damian.net> - 2.0.8-2
- --enable-id64 flag for 64-bit builds

* Sat May 11 2013 Christof Damian <christof@damian.net> - 2.0.8-1
- upstream 2.0.8

* Sat Apr 20 2013 Christof Damian <christof@damian.net> - 2.0.7-1
- upstream 2.0.7
- use tmpfiles.d to create pid directory
- move default log file location to /var/log/sphinx
- use systemd macros BZ 850323

* Wed Mar  6 2013 Michel Salim <salimma@fedoraproject.org> - 2.0.6-1
- Update to 2.0.6
- Remove obsoleted patches

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 14 2012 Jon Ciesla <limburgher@gmail.com> - 2.0.3-1
- New upstream, migrate to systemd, BZ 692157.
- Patched for gcc47.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.9-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 0.9.9-6
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Dec 11 2010 Christof Damian <christof@damian.net> - 0.9.9-4
- add java and php subpackages ( bug 566787 )

* Sat Dec 11 2010 Christof Damian <christof@damian.net> - 0.9.9-3
- change default listen address to localhost ( bug 566792 )
- add ghost for files in /var/run/ ( bug 656694 )

* Wed Jul 14 2010 Christof Damian <christof@damian.net> - 0.9.9-2
- add COPYING file to lib package

* Thu Feb 11 2010 Allisson Azevedo <allisson@gmail.com> 0.9.9-1
- Update to 0.9.9 (#556997).
- Added sphinx-0.9.9-fix_static.patch to fix FTBS.
- Run sphinx searchd as non-root user (#541464).

* Wed Aug 26 2009 Tomas Mraz <tmraz@redhat.com> 0.9.8.1-4
- Rebuild with new openssl

* Wed Aug 12 2009 Allisson Azevedo <allisson@gmail.com> 0.9.8.1-3
- Fixed macros consistency.
- Modified make install to keep timestamps.
- Added libsphinxclient package.

* Fri Aug  7 2009 Allisson Azevedo <allisson@gmail.com> 0.9.8.1-2
- Added sysv init.
- Added logrotate.d entry.

* Thu Jul 30 2009 Allisson Azevedo <allisson@gmail.com> 0.9.8.1-1
- Initial rpm release.
