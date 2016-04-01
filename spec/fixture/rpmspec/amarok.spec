
%define kdewebkit 1
# define to enable optional -nepomukcollection support
%if 0%{?fedora} < 22
%define nepomukcollection 1
%endif

Name:    amarok
Summary: Media player
Version: 2.8.90
Release: 5%{?dist}

# KDE e.V. may determine that future GPL versions are accepted
License: GPLv2 or GPLv3
Url:     http://amarok.kde.org/
#global revision %(echo %{version} | cut -d. -f3)
#if %{revision} >= 50
#global stable unstable
#else
%global stable stable
#endif
Source0: http://download.kde.org/%{stable}/amarok/%{version}/src/amarok-%{version}.tar.xz

# Invoke a browser on the online UserBase documentation instead of KHelpCenter
# for the help contents if the amarok-doc subpackage is not installed.
Patch0:  amarok-2.8.0-onlinedoc.patch

# try to allow build without kdewebkit (like rhel), use QWeb* instead of KWeb*
Patch1: amarok-2.8.0-no_kdewebkit.patch

## upstreamable patches
# make mysql_found non-fatal
Patch100: amarok-2.8.90-mysql_found.patch
# fix detection of mysql_libraries in non-mysqlconfig case
Patch101: amarok-2.8.90-find_mysql.patch

## upstream patches
Patch3: 0003-Fix-TagLib-version-check.patch

BuildRequires: curl-devel
BuildRequires: desktop-file-utils
## non-modular MusicBrainz-based audio fingerprint tag lookup support :( 
#BuildRequires: ffmpeg-devel libofa-devel
BuildRequires: gettext
BuildRequires: kdelibs4-devel >= 4.9
%if 0%{?kdewebkit}
BuildRequires: kdelibs4-webkit-devel
%endif
%if 0%{?fedora} > 21
BuildRequires: libappstream-glib
%endif
BuildRequires: mysql-devel
BuildRequires: mysql-embedded-devel
BuildRequires: pkgconfig(gdk-pixbuf-2.0)
BuildRequires: pkgconfig(glib-2.0) pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(libxml-2.0)
BuildRequires: pkgconfig(phonon) >= 4.5.0
BuildRequires: pkgconfig(qca2)
BuildRequires: pkgconfig(QJson)
BuildRequires: pkgconfig(QtWebKit)
BuildRequires: pkgconfig(taglib) >= 1.6
BuildRequires: pkgconfig(taglib-extras) >= 1.0.1

%if 0%{?fedora}
BuildRequires: kf5-rpm-macros
Requires:      kf5-filesystem
BuildRequires: liblastfm-devel >= 1.0.3
BuildRequires: pkgconfig(libmygpo-qt) >= 1.0.7
BuildRequires: pkgconfig(loudmouth-1.0)
BuildRequires: pkgconfig(libmtp) >= 0.3.0
Requires: kio_mtp
BuildRequires: pkgconfig(libgpod-1.0) >= 0.7.0
Requires: ifuse
# not strictly required at buildtime, but if it's not available here,
# then you're hosed at runtime anyway
BuildRequires: clamz
Requires: clamz
Requires: kio-upnp-ms
# only in fedora, https://bugzilla.redhat.com/1232818
Requires: audiocd-kio
%endif
BuildRequires: qtscriptbindings
Requires: qtscriptbindings%{?_isa}
Requires: %{name}-utils = %{version}-%{release}
Requires: kde-runtime
Requires: media-player-info

Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%if ! 0%{?nepomukcollection}
BuildConflicts: nepomuk-core-devel
Obsoletes: amarok-nepomukcollection < %{version}-%{release}
%endif

%description
Amarok is a multimedia player with:
 - fresh playlist concept, very fast to use, with drag and drop
 - plays all formats supported by the various engines
 - audio effects, like reverb and compressor
 - compatible with the .m3u and .pls formats for playlists
 - nice GUI, integrates into the KDE look, but with a unique touch

%package libs
Summary: Runtime libraries for %{name}
Requires: %{name} = %{version}-%{release}
%{?_qt4_version:Requires: qt4%{?_isa} >= %{_qt4_version}}
%description libs
%{summary}.

%package utils
Summary: Amarok standalone utilities
%description utils 
%{summary}, including amarokcollectionscanner.

%package doc
Summary: Application handbook, documentation, translations
# for upgrade path
Obsoletes: amarok < 2.5.0-4
Requires:  %{name} = %{version}-%{release}
BuildArch: noarch
%description doc
%{summary}.

%if 0%{?nepomukcollection}
%package nepomukcollection
Summary: Nepomuk collection plugin for %{name}
BuildRequires: nepomuk-core-devel
BuildRequires: pkgconfig(soprano)
# for upgrade path
Obsoletes: amarok < 2.8.0-4
Requires: %{name} = %{version}-%{release}
%description nepomukcollection
%{summary}.
%endif


%prep
%setup -q 

%patch0 -p1 -b .onlinedoc
%if ! 0%{?kdewebkit}
%patch1 -p1 -b .no_kdewebkit
%endif

## upstream
%patch3 -p1 -b .taglib_version_check

## upstreamable
#patch100 -p1 -b .mysql_found
%patch101 -p1 -b .find_mysql


%build
mkdir %{_target_platform}
pushd %{_target_platform}
# force non-use of MYSQLCONFIG, to avoid (potential bogus) stuff from: mysql_config --libmysqld-libs
%{cmake_kde4} .. \
  -DMYSQLCONFIG_EXECUTABLE:BOOL=OFF
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

%if 0%{?fedora}
mkdir -p %{buildroot}%{_kf5_datadir}/solid/actions/
cp -alf \
  %{buildroot}%{_kde4_appsdir}/solid/actions/amarok-play-audiocd.desktop \
  %{buildroot}%{_kf5_datadir}/solid/actions/
mkdir -p %{buildroot}%{_kf5_datadir}/kservices5/ServiceMenus
cp -alf \
  %{buildroot}%{_kde4_datadir}/kde4/services/ServiceMenus/amarok_append.desktop \
  %{buildroot}%{_kf5_datadir}/kservices5/ServiceMenus/
%endif

%find_lang amarok --with-kde --without-mo && mv amarok.lang amarok-doc.lang
%find_lang amarok
%find_lang amarokcollectionscanner_qt 
%find_lang amarokpkg && cat amarokpkg.lang >> amarok.lang
%find_lang amarok_scriptengine_qscript && cat amarok_scriptengine_qscript.lang >> amarok.lang

# unpackaged files
rm -fv %{buildroot}%{_kde4_libdir}/libamarok{-sqlcollection,_taglib,core,lib,plasma,pud,ocsclient,shared,-transcoding}.so


%check
%if 0%{?fedora} > 20
appstream-util validate-relax --nonet %{buildroot}%{_kde4_datadir}/appdata/%{name}.appdata.xml
%endif
desktop-file-validate %{buildroot}%{_kde4_datadir}/applications/kde4/amarok.desktop
desktop-file-validate %{buildroot}%{_kde4_datadir}/applications/kde4/amarok_containers.desktop


%post
touch --no-create %{_kde4_iconsdir}/hicolor &> /dev/null || :
touch --no-create %{_datadir}/mime/packages &> /dev/null || :

%posttrans
gtk-update-icon-cache %{_kde4_iconsdir}/hicolor &> /dev/null || :
update-desktop-database -q &> /dev/null ||:
update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
touch --no-create %{_kde4_iconsdir}/hicolor &> /dev/null || :
gtk-update-icon-cache %{_kde4_iconsdir}/hicolor &> /dev/null || :
update-desktop-database -q &> /dev/null ||:
touch --no-create %{_datadir}/mime/packages &> /dev/null || :
update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :
fi

%files -f amarok.lang
%doc AUTHORS ChangeLog README
%license COPYING
%{_kde4_bindir}/amarok
%{_kde4_bindir}/amarokpkg
%{_kde4_bindir}/amarok_afttagger
%if 0%{?fedora}
%{_kde4_bindir}/amarokmp3tunesharmonydaemon
%{_kf5_datadir}/solid/actions/amarok-play-audiocd.desktop
%{_kf5_datadir}/kservices5/ServiceMenus/amarok_append.desktop
%endif
%{_kde4_bindir}/amzdownloader
%{_kde4_appsdir}/amarok/
%{_kde4_appsdir}/kconf_update/amarok*
%{_kde4_appsdir}/desktoptheme/default/widgets/*
%{_kde4_appsdir}/solid/actions/amarok-play-audiocd.desktop
%{_kde4_configdir}/amarok.knsrc
%{_kde4_configdir}/amarok_homerc
%{_kde4_configdir}/amarokapplets.knsrc
%{_kde4_datadir}/appdata/%{name}.appdata.xml
%{_kde4_datadir}/applications/kde4/amarok.desktop
%{_kde4_datadir}/applications/kde4/amarok_containers.desktop
%{_kde4_datadir}/applications/kde4/amzdownloader.desktop
%{_kde4_datadir}/config.kcfg/amarokconfig.kcfg
%{_kde4_datadir}/kde4/services/amarok-containment-*.desktop
%{_kde4_datadir}/kde4/services/amarok-context-applet-*.desktop
%{_kde4_datadir}/kde4/services/amarok-data-engine-*.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-audiocdcollection.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-daapcollection.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-mysqlcollection.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-playdarcollection.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-umscollection.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-upnpcollection.desktop
%{_kde4_datadir}/kde4/services/amarok_importer-amarok.desktop
%{_kde4_datadir}/kde4/services/amarok_importer-banshee.desktop
%{_kde4_datadir}/kde4/services/amarok_importer-clementine.desktop
%{_kde4_datadir}/kde4/services/amarok_importer-fastforward.desktop
%{_kde4_datadir}/kde4/services/amarok_importer-itunes.desktop
%{_kde4_datadir}/kde4/services/amarok_importer-rhythmbox.desktop
%{_kde4_datadir}/kde4/services/amarok_service_*.desktop
%{_kde4_datadir}/kde4/services/amarok_storage-mysqlestorage.desktop
%{_kde4_datadir}/kde4/services/amarok_storage-mysqlserverstorage.desktop
%{_kde4_datadir}/kde4/services/*.protocol
%{_kde4_datadir}/kde4/services/ServiceMenus/amarok_append.desktop
%{_kde4_datadir}/kde4/servicetypes/*.desktop
%{_kde4_iconsdir}/hicolor/*/*/*
%{_kde4_libdir}/kde4/amarok_collection-audiocdcollection.so
%{_kde4_libdir}/kde4/amarok_collection-daapcollection.so
%if 0%{?fedora}
%{_kde4_datadir}/kde4/services/amarok_collection-ipodcollection.desktop
%{_kde4_datadir}/kde4/services/amarok_collection-mtpcollection.desktop
%{_kde4_libdir}/kde4/amarok_collection-ipodcollection.so
%{_kde4_libdir}/kde4/amarok_collection-mtpcollection.so
%endif
%{_kde4_libdir}/kde4/amarok_collection-mysqlcollection.so
%{_kde4_libdir}/kde4/amarok_collection-playdarcollection.so
%{_kde4_libdir}/kde4/amarok_collection-umscollection.so
%{_kde4_libdir}/kde4/amarok_collection-upnpcollection.so
%{_kde4_libdir}/kde4/amarok_containment_*.so
%{_kde4_libdir}/kde4/amarok_context_applet_*.so
%{_kde4_libdir}/kde4/amarok_data_engine_*.so
%{_kde4_libdir}/kde4/amarok_importer-amarok.so
%{_kde4_libdir}/kde4/amarok_importer-banshee.so
%{_kde4_libdir}/kde4/amarok_importer-clementine.so
%{_kde4_libdir}/kde4/amarok_importer-fastforward.so
%{_kde4_libdir}/kde4/amarok_importer-itunes.so
%{_kde4_libdir}/kde4/amarok_importer-rhythmbox.so
%{_kde4_libdir}/kde4/amarok_service_*.so
%{_kde4_libdir}/kde4/amarok_storage-mysqlestorage.so
%{_kde4_libdir}/kde4/amarok_storage-mysqlserverstorage.so
%{_kde4_libdir}/kde4/kcm_amarok_service*.so
%{_datadir}/dbus-1/interfaces/*.xml
%{_datadir}/mime/packages/amzdownloader.xml

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs
%{_kde4_libdir}/libamarokcore.so.1*
%{_kde4_libdir}/libamaroklib.so.1*
%{_kde4_libdir}/libamarokocsclient.so.4*
%{_kde4_libdir}/libamarokpud.so.1*
%{_kde4_libdir}/libamarokshared.so.1*
%{_kde4_libdir}/libamarok-sqlcollection.so.1*
%{_kde4_libdir}/libamarok-transcoding.so.1*
# private libs
%if 0%{?fedora}
%{_kde4_libdir}/libamarok_service_lastfm_shared.so
%endif
%{_kde4_libdir}/libampache_account_login.so

%files utils -f amarokcollectionscanner_qt.lang
%{_kde4_bindir}/amarokcollectionscanner

%files doc -f amarok-doc.lang

%if 0%{?nepomukcollection}
%files nepomukcollection
%{_kde4_libdir}/kde4/amarok_collection-nepomukcollection.so
%{_kde4_datadir}/kde4/services/amarok_collection-nepomukcollection.desktop
%endif


%changelog
* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.8.90-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Dec 29 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.90-4
- add support for kf5 solid/actions,ServiceMenus

* Thu Dec 10 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.90-3
- workaround 'mysql_config --libmysqld-libs' madness (#1290517)

* Thu Dec 10 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.90-2
- make kde-runtime dep unversioned, use %%license

* Fri Sep 11 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.90-1
- 2.8.90

* Fri Aug 28 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-19
- backport upstream FindTaglib.cmake fix

* Mon Jun 29 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-18
- Amarok has an unmet dependency on rhel7: audiocd-kio (#1232818)

* Sun Jun 28 2015 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-17
- pull in upstream fixes for wikipedia plugin (kde#349313)

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.0-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 2.8.0-15
- Rebuilt for GCC 5 C++11 ABI change

* Fri Feb 20 2015 Rex Dieter <rdieter@fedoraproject.org> - 2.8.0-14
- backport gl crasher workaround (kde#323635)
- deprecate -nepomukcollection (f22+)

* Sat Nov 08 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-13
- use fresher upstream appdata (translations mostly)

* Fri Nov 07 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-12
- pull in upstream (master/ branch) appdata

* Sat Oct 18 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-11
- drop Requires: moodbar (which still pulls in gstreamer-0.10)

* Wed Oct 01 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-10
- rebuild (libmygpo-qt test)

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 08 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-8
- scriptet polish

* Thu Jul 03 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-7
- optimize mimeinfo scriplet

* Thu Jun 19 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-6
- work on epel7 support, BR: kdelibs4-webkit-devel

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 14 2014 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-4
- -nepomukcollection subpkg

* Tue Aug 27 2013 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-3.1
- BR: libmygpo-qt-devel >= 1.0.7

* Sat Aug 17 2013 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-3
- Requires: moodbar

* Fri Aug 16 2013 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-2
- (Build)Requires: clamz

* Thu Aug 15 2013 Rex Dieter <rdieter@fedoraproject.org> 2.8.0-1
- 2.8.0

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 2.7.90-2
- Perl 5.18 rebuild

* Thu Aug 01 2013 Rex Dieter <rdieter@fedoraproject.org> 2.7.90-1
- 2.7.90

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 2.7.1-3
- Perl 5.18 rebuild

* Fri May 17 2013 Rex Dieter <rdieter@fedoraproject.org> 2.7.1-2
- drop already-included qtwebkit/wikipedia fixer

* Thu May 16 2013 Rex Dieter <rdieter@fedoraproject.org> 2.7.1-1
- 2.7.1

* Mon May 13 2013 Rex Dieter <rdieter@fedoraproject.org> - 2.7.0-4
- backport a few upstream fixes, in particular...
- workaround for qtwebkit/wikipedia related crashes (kde #319371)

* Sat Feb 02 2013 Rex Dieter <rdieter@fedoraproject.org> 2.7.0-3
- rebuild (mariadb)

* Mon Jan 28 2013 Rex Dieter <rdieter@fedoraproject.org> 2.7.0-2
- Requires: kio_mtp, kio-upnp-ms

* Thu Jan 17 2013 Rex Dieter <rdieter@fedoraproject.org> 2.7.0-1
- 2.7.0

* Sat Dec 15 2012 Rex Dieter <rdieter@fedoraproject.org> - 2.6.90-2
- up build deps (nepomuk-core, liblastfm)
- changelog: prune, fix bad dates

* Fri Dec 14 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.90-1
- 2.6.90

* Tue Nov 27 2012 Jan Grulich <jgrulich@redhat.com> 2.6.0-7
- rebuild (qjson)

* Sat Nov 24 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.0-6
- rebuild (qjson)

* Tue Sep 11 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.0-5
- -doc: update summary to mention translations

* Fri Sep 7 2012 Dominique Bribanick <chepioq@gmail.com> 2.6.0-4
- add patch for french translation (#855655)

* Sat Aug 25 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.0-3
- Requires: kdemultimedia-kio_audiocd/audiocd-kio

* Wed Aug 22 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.0-2.1
- use liblastfm1 on f16/f17 too

* Sun Aug 12 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.0-2
- Requires: media-player-info

* Sat Aug 11 2012 Rex Dieter <rdieter@fedoraproject.org> 2.6.0-1
- 2.6.0

* Thu Aug 02 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.96-1
- 2.5.96 (2.6rc1)

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.90-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.90-5
- backport upstream commit to disable polling (kde#289462)

* Sat Jul 14 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.90-4
- update kdelibs/phonon dep versions

* Tue Jul 03 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.90-3
- add reviewboard patch to support liblastfm1

* Tue Jul 03 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.90-2
- rebuild (liblastfm)

* Wed May 30 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.90-1
- 2.5.90

* Wed Mar 21 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.0-9
- new iteration of proxy_loading patch (kde#295199)

* Tue Mar 13 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.0-8
- Load all XSPF tracks (kde#295199)

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-7
- Rebuilt for c++ ABI breakage

* Sun Jan 29 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 2.5.0-6
- help: invoke a browser on the online UserBase doc if amarok-doc not installed

* Fri Jan 27 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.0-5
- make -doc only handbook, put translations back in main pkg

* Fri Jan 27 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.0-4
- -doc subpkg for large'ish application handbook and translations

* Fri Jan 27 2012 Rex Dieter <rdieter@fedoraproject.org> 2.5.0-3
- fix context view when on kde48 (kde#290123)

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Dec 16 2011 Rex Dieter <rdieter@fedoraproject.org> 2.5.0-1
- 2.5.0

* Mon Nov 14 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.90-1
- 2.4.90

* Wed Nov 09 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.3-4
- pkgconfig-style deps
- drop extraneous/old BR's

* Mon Sep 19 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.3-3
- Wikipedia applet crashes (kde#279813)

* Fri Sep 16 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.3-2
- re-enable libgpod support inadvertantly lost in 2.4.1.90-1

* Sat Jul 30 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.3-1
- 2.4.3

* Sun Jul 24 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.2-2
- don't query kwallet for lastfm credentials on every track change (kde#278177)

* Fri Jul 22 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.2-1
- 2.4.2

* Fri Jul 08 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.1.90-1
- 2.4.1.90
- drop no-longer-needed %%ifarch s390 conditionals

* Fri Jun 10 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.1-4
- drop ancient Obsoletes

* Fri Jun 10 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.1-3
- rebuild (libmtp)

* Tue May 24 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.1-2
- BR: libmygpo-qt-devel

* Fri May 06 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.1-1
- 2.4.1 (final)

* Wed Mar 23 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.0.90-2
- rebuild (mysql)

* Mon Mar 21 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.0.90-1
- 2.4.1 beta1

* Wed Feb 09 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.0-3
- License: GPLv2 or GPLv3 

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 11 2011 Rex Dieter <rdieter@fedoraproject.org> 2.4.0-1
- 2.4.0
- libmtp-hal dependency missing for amarok (#666173)

* Tue Dec 28 2010 Rex Dieter <rdieter@fedoraproject.org> 2.3.90-3
- rebuild (mysql)

* Tue Dec 07 2010 Thomas Janssen <thomasj@fedoraproject.org> 2.3.90-2
- fixed missing libampache

* Mon Dec 06 2010 Thomas Janssen <thomasj@fedoraproject.org> 2.3.90-1
- 2.3.90 (2.4beta1)

* Tue Nov 30 2010 Rex Dieter <rdieter@fedoraproject.org> 2.3.2-7
- recognize audio/flac mimetype too (kde#257488)

* Fri Nov 05 2010 Thomas Janssen <thomasj@fedoraproject.org> 2.3.2-6
- rebuild for new libxml2

* Thu Nov 04 2010 Rex Dieter <rdieter@fedoraproject.org> 2.3.2-5
- appletsize patch
- fix/improve ipod3 support patch
- another collectionscanner patch

* Wed Sep 29 2010 jkeating - 2.3.2-4
- Rebuilt for gcc bug 634757

* Fri Sep 24 2010 Thomas Janssen <thomasj@fedoraproject.org> 2.3.2-3
- added patch to fix scanning qt bug/regression

* Mon Sep 20 2010 Thomas Janssen <thomasj@fedoraproject.org> 2.3.2-2
- added patch to fix BPM tags in flac

* Thu Sep 16 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.2-1
- amarok-2.3.2

* Thu Sep 16 2010 Dan Horák <dan[at]danny.cz> - 2.3.1.90-3
- no libgpod on s390(x)

* Mon Aug 16 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.1.90-2
- fix/patch installation of amarok handbooks

* Mon Aug 16 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.1.90-1
- amarok-2.3.1.90 (2.3.2 beta1)

* Fri Jul 09 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.1-2
- No Notification Area icon for non-KDE desktops (kde#232578,rh#603336)

* Fri May 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.1-1
- amarok-2.3.1

* Sat Apr 17 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.0.90-1
- amarok-2.3.0.90

* Thu Mar 25 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.0-5
- fix mp3 support logic

* Mon Mar 22 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.0-4
- rebuild (libgpod) 

* Mon Mar 22 2010 Rex Dieter <rdieter@fedoraproject.org>  - 2.3.0-3
- workaround info applet crasher (kde#227639,kde#229756)

* Thu Mar 11 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.3.0-2
- fix Source0 URL
- -libs: drop unused/extraneous kdelibs4 dep

* Thu Mar 11 2010 Thomas Janssen <thomasj@fedoraproject.org> 2.3.0-1
- amarok 2.3.0

* Sat Feb 13 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.2.2.90-1
- amarok-2.2.2.90 (2.3beta1)

* Thu Jan 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.2.2-4
- use %%{_kde4_version} provided elsewhere (kde-filesystem)

* Sun Jan 10 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.2.2-3
- collection scan crash patch, take 2 (kde#220532)

* Fri Jan 08 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.2.2-2
- collection scan crash patch (kde#220532)

* Tue Jan 05 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.2.2-1
- amarok-2.2.2

* Thu Dec 10 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.2.1.90-1
- amarok-2.2.1.90 (2.2.2 beta1)

* Mon Nov 23 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.2.1-3 
- rebuild (for qt-4.6.0-rc1, f13+)

* Mon Nov 16 2009 Rex Dieter <rdieter@fedoraproject.org> 2.2.1-2
- playlist_default_layout_fix.diff (kde#211717)

* Wed Nov 11 2009 Rex Dieter <rdieter@fedoraproject.org> 2.2.1-1
- amarok-2.2.1

* Thu Oct 08 2009 Rex Dieter <rdieter@fedoraproject.org> 2.2.0-3
- upstream lyric.patch

* Fri Oct 02 2009 Rex Dieter <rdieter@fedoraproject.org> 2.2.0-2
- Requires: kdebase-runtime (need kio_trash, kcm_phonon, etc)

* Tue Sep 29 2009 Rex Dieter <rdieter@fedoraproject.org> 2.2.0-1
- amarok-2.2.0

* Wed Sep 23 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.90-2.20090923git
- 20090923git snapshot

* Mon Sep 21 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.90-1
- amarok-2.1.90 (2.2rc1)

* Thu Sep 17 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.85-2
- BR: taglib-devel >= 1.6, taglib-extras-devel >= 1.0

* Mon Sep 14 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.85-1
- amarok-2.1.85 (2.2beta2)

* Wed Sep 02 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.80-2
- another lyricwiki fix

* Wed Sep 02 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.80-1
- amarok-2.1.80 (2.2beta1)
- -libs subpkg

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.1.1-5
- rebuilt with new openssl

* Sat Aug 08 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.1-4
- lyricwiki patch (kdebug#202366)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 07 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.1-2
- Requires: qtscriptbindings%%{?_isa}  (#510133)

* Fri Jun 12 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1.1-1
- amarok-2.1.1

* Sat May 30 2009 Rex Dieter <rdieter@fedoraproject.org> 2.1-1
- amarok-2.1

* Mon May 18 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.96-2.20090518
- 20090518svn snapshot

* Mon May 11 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.96-1
- amarok-2.9.96 (2.1 beta2)
- -utilities -> -utils

* Fri Apr 10 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.90-2
- -collectionscanner -> -utilities

* Fri Apr 10 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.90-1
- amarok-2.0.90 (amarok-2.1 beta1)

* Wed Apr 08 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.2-6
- fix lastfm (kdebug#188678, rhbz#494871)
- fix qtscriptgenerator/qtscriptbindings deps

* Tue Apr 07 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.2-5
- enable external qtscriptgenerator/qtscriptbindings
- optimize scriptlets

* Tue Mar 10 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.2-4
- Req: qtscriptgenerator (f11+) (not enabled, pending review)
- use desktop-file-validate

* Fri Mar 06 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.2-3
- add minimal qt4,kdelibs4 deps

* Wed Mar 04 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.2-1
- amarok-2.0.2

* Tue Feb 24 2009 Than Ngo <than@redhat.com> 2.0.1.1-6
- fix build issue against gcc-4.4

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 23 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.1.1-4
- qt45 patch

* Fri Feb 20 2009 Todd Zullinger <tmz@pobox.com> - 2.0.1.1-3
- Rebuild against libgpod-0.7.0
- Drop gtk2-devel BR, libgpod properly requires that now

* Thu Jan 22 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.1.1-2 
- respin (mysql)

* Fri Jan 09 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.1.1-1
- amarok-2.0.1.1

* Tue Jan 06 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.1-1
- amarok-2.0.1

* Tue Dec 09 2008 Rex Dieter <rdieter@fedoraproject.org> - 2.0-2
- respin tarball

* Fri Dec 05 2008 Rex Dieter <rdieter@fedoraproject.org> - 2.0-1
- amarok-2.0 (final, first cut)
