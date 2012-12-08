%define _hotplugdir	%{_prefix}/lib/hotplug

%define	major		19
%define	gpsd_major	0
%define	libname		%mklibname %{name} %{major}
%define libqtname	%mklibname Qgpsmm %{major}
%define develname	%mklibname %{name} -d
%define staticname	%mklibname %{name} -s -d

Name: 	 	gpsd
Summary: 	GPS data translator and GUI
Version:	2.95
Release: 	%mkrel 4
Source0:	http://prdownload.berlios.de/%{name}/%{name}-%{version}.tar.gz
Source1:	gpsd.rules
#Source2:	gpsd.sysconfig
Patch1:		gpsd-2.90-udev.patch
Patch2:		gpsd-2.95-fix-link.patch
Patch3:		gpsd-2.95-silentmake.patch
Patch4:		gpsd.ldflags.patch
URL:		http://gpsd.berlios.de
License:	BSD
Group:		Sciences/Geosciences
Provides:	gps3d
Obsoletes:	gps3d
BuildRequires:  ncurses-devel
BuildRequires:  udev
BuildRequires:	lesstif-devel
BuildRequires:	xmlto
BuildRequires:	dbus-devel
BuildRequires:	dbus-glib-devel
BuildRequires:	python
BuildRequires:	python-devel
BuildRequires:	bluez-devel
BuildRequires:	qt4-devel
Requires:	%{name}-python = %{version}-%{release}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
gpsd is a service daemon that mediates access to a GPS sensor
connected to the host computer by serial or USB interface, making its
data on the location/course/velocity of the sensor available to be
queried on TCP port 2947 of the host computer.  With gpsd, multiple
GPS client applications (such as navigational and wardriving software)
can share access to a GPS without contention or loss of data.  Also,
gpsd responds to queries with a format that is substantially easier to
parse than NMEA 0183.  A client library is provided for applications.

After installing this RPM, gpsd will automatically connect to USB
GPSes when they are plugged in and requires no configuration.  For
serial GPSes, you will need to start gpsd by hand.  Once connected,
the daemon automatically discovers the correct baudrate, stop bits,
and protocol. The daemon will be quiescent when there are no
clients asking for location information, and copes gracefully when the
GPS is unplugged and replugged.

%package -n	%{libname}
Summary:	Libraries for gpsd
Group:		System/Libraries
Obsoletes:	%{mklibname gpsd 15} > 2.34

%description -n	%{libname}
gpsd is a service daemon that mediates access to a GPS sensor
connected to the host computer by serial or USB interface, making its
data on the location/course/velocity of the sensor available to be
queried on TCP port 2947 of the host computer.  With gpsd, multiple
GPS client applications (such as navigational and wardriving software)
can share access to a GPS without contention or loss of data.  Also,
gpsd responds to queries with a format that is substantially easier to
parse than NMEA 0183.  A client library is provided for applications.

After installing this RPM, gpsd will automatically connect to USB
GPSes when they are plugged in and requires no configuration.  For
serial GPSes, you will need to start gpsd by hand.  Once connected,
the daemon automatically discovers the correct baudrate, stop bits,
and protocol. The daemon will be quiescent when there are no
clients asking for location information, and copes gracefully when the
GPS is unplugged and replugged.

%package -n     %{libqtname}
Summary:        Qt bindings for gpsd
Group:          System/Libraries

%description -n %{libqtname}
This package contains Qt bindings for gpsd.

%package -n	%{develname}
Summary:	Client libraries in C and Python for talking to a running gpsd or GPS
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}
Requires:	%{libqtname} = %{version}
Obsoletes:	%{mklibname gpsd 15 -d}

%description -n	%{develname}
This package provides C header files for the gpsd shared libraries
that manage access to a GPS for applications; also Python modules.
You will need to have gpsd installed for it to work.

%package -n	%{staticname}
Summary:	Static libraries for gpsd
Group:		Development/C
Provides:	%{name}-static-devel = %{version}-%{release}
Provides:	lib%{name}-static-devel = %{version}-%{release}
Requires:	%{develname} = %{version}
Obsoletes:	%{mklibname gpsd 15 -s -d}

%description -n	%{staticname}
This package provides C header files for the gpsd shared libraries
that manage access to a GPS for applications; also Python modules.
You will need to have gpsd installed for it to work.

%package	clients
Summary:	Clients for gpsd with an X interface
Group:		Sciences/Geosciences

%description	clients
xgps is a simple test client for gpsd with an X interface. It displays
current GPS position/time/velocity information and (for GPSes that
support the feature) the locations of accessible satellites.

xgpsspeed is a speedometer that uses position information from the GPS.
It accepts an -h option and optional argument as for gps, or a -v option
to dump the package version and exit. Additionally, it accepts -rv
(reverse video) and -nc (needle color) options.

%package	python
Summary:	Python bindings for gpsd
Group:		Development/Python
Requires:	%{libname} = %{version}

%description	python
This package contains the Python bindings for gpsd. It will be needed
for any applications that interface with gpsd via python.

%prep
%setup -q
%patch1 -p1 -b .udev
%patch2 -p0 -b .link
%patch3 -p1 -b .make
%patch4 -p2 -b .ldflags

%build
export LDFLAGS="$LDFLAGS -lbluetooth"
%configure2_5x --enable-dbus --enable-bluetooth

%make

%install
rm -rf %{buildroot}

%makeinstall_std

# additional gpsd files
#mkdir -p %{buildroot}%{_datadir}/X11/app-defaults/
#install -m644 xgpsspeed.ad %{buildroot}%{_datadir}/X11/app-defaults/xgpsspeed

mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d
install -m644 %{SOURCE1} %{buildroot}%{_sysconfdir}/udev/rules.d/70-gpsd.rules

mkdir -p %{buildroot}%{_sysconfdir}/udev/agents.d/usb
install -m755 gpsd.hotplug %{buildroot}%{_sysconfdir}/udev/agents.d/usb/gpsd

#install -m755 gps.py -D %{buildroot}%{_libdir}/python${PYVERSION}/site-packages/gps.py

# init scripts
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/init.d
%{__install} -p -m 0755 packaging/rpm/gpsd.init \
	%{buildroot}%{_sysconfdir}/init.d/gpsd

%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -p -m 0644 packaging/rpm/gpsd.sysconfig \
	%{buildroot}%{_sysconfdir}/sysconfig/gpsd

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}-clients.desktop << EOF
[Desktop Entry]
Name=XGPS
Comment=XGPS
Exec=xgps
Icon=communications_section
Terminal=false
Type=Application
StartupNotify=true
Categories=Science;Geology;
EOF

#remove unpackaged file
#rm -f %{buildroot}%{_libdir}/python/site-packages/gps.py

#put the python file(s) in the right place (it's arch-dependent)

# fixme: may need to be adapted to include other 64-bit arches, I'm
# not sure what directory they use - AdamW 2007/07
%ifarch x86_64
mkdir -p %{buildroot}%{py_platsitedir}
mv %{buildroot}%{py_puresitedir}/* %{buildroot}%{py_platsitedir}
%endif

rm -rf %{buildroot}%{_libdir}/*.la

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%post clients
%update_menus
%endif

%if %mdkversion < 200900
%postun clients
%clean_menus
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README
%{_sbindir}/gpsd
%{_bindir}/gpscat
%{_bindir}/gpsctl
%{_bindir}/gpsprof
%{_bindir}/gpsmon
%{_bindir}/gpsdecode
%{_mandir}/man8/gpsd.8*
%{_mandir}/man1/gpsprof.1*
%{_mandir}/man1/gps.1*
%{_mandir}/man1/gpscat.1*
%{_mandir}/man1/gpsctl.1*
%{_mandir}/man1/gpsmon.1*
%{_mandir}/man1/gpsdecode.1*
%{_mandir}/man5/rtcm*.5*
%{_mandir}/man5/srec.5*
%{_sysconfdir}/init.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_sysconfdir}/udev/agents.d/usb/gpsd
%{_sysconfdir}/udev/rules.d/70-gpsd.rules

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libgps.so.%{major}*
%{_libdir}/libgpsd.so.%{gpsd_major}*

%files -n %{libqtname}
%defattr(-,root,root)
%{_libdir}/libQgpsmm.so.%{major}*

%files -n %{develname}
%defattr(-,root,root,-)
%doc TODO
%{_includedir}/gps.h
%{_includedir}/libgpsmm.h
%{_includedir}/gpsd.h
%{_libdir}/libgps.so
%{_libdir}/libgpsd.so
%{_libdir}/libQgpsmm.so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man1/gpsfake.1*
%{_mandir}/man3/libgps.3*
%{_mandir}/man3/libgpsmm.3*
%{_mandir}/man3/libgpsd.3*
%{_bindir}/gpsfake

%files -n %{staticname}
%defattr(-,root,root)
%{_libdir}/*.a

%files clients
%defattr(-,root,root,-)
%{_bindir}/xgps
%{_bindir}/cgps
%{_bindir}/gpspipe
%{_bindir}/xgpsspeed
%{_bindir}/gpxlogger
%{_bindir}/lcdgps
%{_mandir}/man1/xgps.1*
%{_mandir}/man1/cgps.1*
#%{_mandir}/man1/cgpxlogger.1*
%{_mandir}/man1/gpspipe.1*
%{_mandir}/man1/lcdgps.1.*
%{_mandir}/man1/xgpsspeed.1*
#%{_datadir}/X11/app-defaults/xgpsspeed
%{_datadir}/applications/mandriva-%{name}-clients.desktop

%files python
%defattr(-,root,root,-)
%{py_platsitedir}/*


%changelog
* Sun May 08 2011 Funda Wang <fwang@mandriva.org> 2.95-3mdv2011.0
+ Revision: 672483
- fix python name

  + Oden Eriksson <oeriksson@mandriva.com>
    - mass rebuild

* Tue Nov 02 2010 Michael Scherer <misc@mandriva.org> 2.95-2mdv2011.0
+ Revision: 592389
- rebuild for python 2.7

* Tue Aug 03 2010 Funda Wang <fwang@mandriva.org> 2.95-1mdv2011.0
+ Revision: 565361
- X11-devel is of no use
- fix linkage
- include qt package
- drop unused lines

  + Emmanuel Andry <eandry@mandriva.org>
    - fix files list
    - enable experimental bluetooth support
    - New version 2.95
    - drop p2, fixed differently upstream
    - drop SOURCE2, using upstream sysconfig file
    - update files list

* Fri Jun 18 2010 Anssi Hannula <anssi@mandriva.org> 2.94-3mdv2010.1
+ Revision: 548288
- fix app-defaults location (fixes upgrade)
- install a proper app-defaults file instead of copies of the program
  binaries

* Wed Apr 28 2010 Christophe Fergeau <cfergeau@mandriva.com> 2.94-2mdv2010.1
+ Revision: 540028
- rebuild so that shared libraries are properly stripped again

* Sun Apr 25 2010 Emmanuel Andry <eandry@mandriva.org> 2.94-1mdv2010.1
+ Revision: 538692
- New version 2.94
- diff p2 to fix libusb.h detection
- update files list

* Mon Mar 22 2010 Emmanuel Andry <eandry@mandriva.org> 2.92-1mdv2010.1
+ Revision: 526634
- New version 2.92
- use upstream init
- update files list

* Wed Mar 03 2010 Emmanuel Andry <eandry@mandriva.org> 2.91-1mdv2010.1
+ Revision: 513838
- New version 2.91

* Tue Jan 19 2010 Emmanuel Andry <eandry@mandriva.org> 2.90-1mdv2010.1
+ Revision: 493790
- New version 2.90
- New major 19
- rediff p1
- add init and sysconfig (fedora)
- update files list

  + Helio Chissini de Castro <helio@mandriva.com>
    - Avoid recursion in rpm build when used subrel for updates/backports.

* Wed Jul 01 2009 Wanderlei Cavassin <cavassin@mandriva.com.br> 2.39-1mdv2010.0
+ Revision: 391378
- New version 2.39
  Updated file list (some utilities have been renamed/merged)

* Thu May 21 2009 Guillaume Rousse <guillomovitch@mandriva.org> 2.38-2mdv2010.0
+ Revision: 378540
- rebuild

* Fri Feb 20 2009 Emmanuel Andry <eandry@mandriva.org> 2.38-1mdv2009.1
+ Revision: 343436
- New version 2.38
- update files list
- disable parallel build

* Fri Dec 26 2008 Adam Williamson <awilliamson@mandriva.org> 2.37-2mdv2009.1
+ Revision: 319535
- rebuild with python 2.6

* Fri Oct 10 2008 Adam Williamson <awilliamson@mandriva.org> 2.37-1mdv2009.1
+ Revision: 291442
- python sub-package requires python (duh)
- main package requires python sub-package (gpscat needs it)
- new major 17
- new version 2.37

  + Funda Wang <fwang@mandriva.org>
    - New version 2.37
    - license should be BSD

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Oct 23 2007 Funda Wang <fwang@mandriva.org> 2.34-2mdv2008.1
+ Revision: 101509
- fix libmajor

  + Thierry Vignaud <tv@mandriva.org>
    - do not harcode icon extension

* Thu Jul 19 2007 Adam Williamson <awilliamson@mandriva.org> 2.34-1mdv2008.0
+ Revision: 53570
- more python fixing...
- put python .so file in the right place
- split python stuff to a separate package, fix lists again
- fix file list
- clean up docs
- buildrequires python-devel
- buildrequires python
- fix tarball
- rebuild with new lesstif
- new devel policy
- drop old menu file and X-Mandriva category
- new release 2.34


* Sat Dec 09 2006 Emmanuel Andry <eandry@mandriva.org> 2.33-1mdv2007.0
+ Revision: 93973
- New version 2.33
  drop patches 2 and 3

* Sat Dec 09 2006 Emmanuel Andry <eandry@mandriva.org> 2.30-8mdv2007.1
+ Revision: 93950
- add buildrequires dbus-glib-devel
  fix xdg menu
- rebuild for missing x86_64 libdbus
- Import gpsd

* Sat Aug 05 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.30-7mdv2007.0
- rebuild against new dbus
- add xdg menu

* Sun Jun 25 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 2.30-6
- add BuildRequires: lesstif-devel xmlto

* Thu May 11 2006 Frederic Crozat <fcrozat@mandriva.com> 2.30-5mdk
- Patch3: fix build on x86-64

* Fri Jan 27 2006 Frederic Crozat <fcrozat@mandriva.com> 2.30-4mdk
- Rebuild with latest dbus

* Fri Nov 04 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.30-3mdk
- Fix BuildRequires

* Fri Nov 04 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.30-2mdk
- Fix BuildRequires

* Thu Nov 03 2005 Frederic Crozat <fcrozat@mandriva.com> 2.30-1mdk
- Release 2.30 
- Remove patch0 (merged upstream)
- Patch2: fix build with dbus 0.50
- fix rpmlint errors

* Sun Aug 28 2005 Olivier Blin <oblin@mandriva.com> 2.28-2mdk
- Patch1: don't write remover script and update script name in usermap
- move hotplug script to %%{_sysconfdir}/udev/agents.d/usb/gpsd
- convert usermap to udev rule

* Wed Aug 10 2005 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.28-1mdk
- 2.28
- bump major
- fix build with gcc 4 (P0, from debian)
- fix permission on hotplug script

* Sat Aug 06 2005 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.25-3mdk
- fix path to hotplug script

* Fri Jun 17 2005 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.25-2mdk
- don't use dbus on 10.2 and older releases

* Fri Jun 17 2005 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.25-1mdk
- 2.25
- name changed, new spec, obsoletes gps3d

* Sun Jun 06 2004 Austin Acton <austin@mandrake.org> 1.20-3mdk
- fix menu

