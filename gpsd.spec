%define name	gpsd
%define version	2.33
%define rel	1
%define release %mkrel %{rel}

%define _hotplugdir %{_prefix}/lib/hotplug

%define	py_ver	%(python -V 2>&1 | cut -f2 -d" " | cut -f1,2 -d".")
%define	major	15
%define	libname	%mklibname %{name} %{major}

Name: 	 	%{name}
Summary: 	GPS data translator and GUI
Version: 	%{version}
Release: 	%{release}

Source0:	%{name}-%{version}.tar.bz2
Patch1:		gpsd-2.28-udev.patch
# (fc) 2.30-1mdk fix build with dbus 0.50
#Patch2:		gpsd-2.30-dbus050.patch.bz2
# (fc) 2.30-5mdk fix build on x86-64
#Patch3:		gpsd-2.30-fixbuild.patch.bz2
URL:		http://www.pygps.org/gpsd/gpsd.html
License:	GPL
Group:		Sciences/Geosciences
Provides:	gps3d
Obsoletes:	gps3d
BuildRequires:	X11-devel
BuildRequires:  ncurses-devel
BuildRequires:  udev-tools
BuildRequires:  automake1.9
BuildRequires:	lesstif-devel
BuildRequires:	xmlto
BuildRequires:	dbus-devel
BuildRequires:	dbus-glib-devel
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

%description -n	%{libname}
Libraries for gpsd.

%package -n	%{libname}-devel
Summary:	Client libraries in C and Python for talking to a running gpsd or GPS
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n	%{libname}-devel
This package provides C header files for the gpsd shared libraries
that manage access to a GPS for applications; also Python modules.
You will need to have gpsd installed for it to work.

%package -n	%{libname}-static-devel
Summary:	Static libraries for gpsd
Group:		Development/C
Provides:	%{name}-static-devel = %{version}-%{release}
Provides:	lib%{name}-static-devel = %{version}-%{release}
Requires:	%{libname}-devel = %{version}

%description -n	%{libname}-static-devel
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

%prep
%setup -q
%patch1 -p1 -b .udev
#%patch2 -p1 -b .dbus050
#%patch3 -p1 -b .fixbuild

#needed by patch3
aclocal-1.9
touch NEWS ChangeLog
automake-1.9 

%build
%configure2_5x \
%if %mdkversion > 1020
	--enable-dbus
%endif

%make
										
%install
rm -rf %{buildroot}

%makeinstall
install -m644 xgps.ad -D %{buildroot}%{_libdir}/X11/app-defaults/xgps/xgps
install -m644 xgpsspeed.ad -D %{buildroot}%{_libdir}/X11/app-defaults/xgpsspeed

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d
/usr/sbin/udev_import_usermap --no-modprobe usb gpsd.usermap > $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/70-gpsd.rules
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/udev/agents.d/usb
install -m755 gpsd.hotplug $RPM_BUILD_ROOT%{_sysconfdir}/udev/agents.d/usb/gpsd

install -m755 gps.py -D %{buildroot}%{_libdir}/python${PYVERSION}/site-packages/gps.py


#menu
mkdir -p %{buildroot}%{_menudir}
cat << EOF > %{buildroot}%{_menudir}/%{name}-clients
?package(%{name}-clients): command="xgps" icon="communications_section.png" needs="x11" title="XGPS" longtitle="XGPS" section="More Applications/Sciences/Geosciences" xdg="true"
EOF

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
Categories=X-MandrivaLinux-Sciences-Geosciences;Science;Geology;
EOF

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post clients
%update_menus

%postun clients
%clean_menus

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README
%{_sbindir}/gpsd
%{_bindir}/gpsprof
%{_bindir}/sirfmon
%{_bindir}/gpsflash
%{_bindir}/rtcmdecode
%{_mandir}/man8/gpsd.8*
%{_mandir}/man1/gpsflash.1*
%{_mandir}/man1/gpsprof.1*
%{_mandir}/man1/gps.1*
%{_mandir}/man1/sirfmon.1*
%{_mandir}/man1/rtcm*.1*
%{_mandir}/man5/rtcm*.5*
%{_mandir}/man5/srec.5*
%{_sysconfdir}/udev/agents.d/usb/gpsd
%{_sysconfdir}/udev/rules.d/70-gpsd.rules

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libgps.so.*

%files -n %{libname}-devel
%defattr(-,root,root,-)
%doc README HACKING TODO
%{_includedir}/gps.h
%{_includedir}/libgpsmm.h
%{_includedir}/gpsd.h
%{_libdir}/libgps.la
%{_libdir}/libgps.so
%{_mandir}/man1/gpsfake.1*
%{_mandir}/man3/libgps.3*
%{_mandir}/man3/libgpsmm.3*
%{_mandir}/man3/libgpsd.3*
%{_bindir}/gpsfake
%{_libdir}/python*/site-packages/gps.py*

%files -n %{libname}-static-devel
%defattr(-,root,root)
%{_libdir}/libgps.a

%files clients
%defattr(-,root,root,-)
%{_bindir}/xgps
%{_bindir}/cgps
%{_bindir}/gpspipe
%{_bindir}/xgpsspeed
%{_bindir}/gpxlogger
%{_bindir}/cgpxlogger
%{_mandir}/man1/xgps.1*
%{_mandir}/man1/cgps.1*
%{_mandir}/man1/cgpxlogger.1*
%{_mandir}/man1/gpspipe.1*
%{_mandir}/man1/xgpsspeed.1*
%{_libdir}/X11/app-defaults/xgps
%{_libdir}/X11/app-defaults/xgpsspeed
%{_menudir}/*
%{_datadir}/applications/mandriva-%{name}-clients.desktop


