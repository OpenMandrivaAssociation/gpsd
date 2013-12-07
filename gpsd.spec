%define _hotplugdir	%{_prefix}/lib/hotplug

%define	gpsmaj	19
%define	major	0
%define	libgps		%mklibname gps %{gpsmaj}
%define	libname		%mklibname %{name} %{major}
%define libqtname	%mklibname Qgpsmm %{gpsmaj}
%define devname		%mklibname %{name} -d

Summary: 	GPS data translator and GUI
Name: 	 	gpsd
Version:	2.95
Release: 	10
License:	BSD
Group:		Sciences/Geosciences
Url:		http://gpsd.berlios.de
Source0:	http://prdownload.berlios.de/%{name}/%{name}-%{version}.tar.gz
Source1:	gpsd.rules
#Source2:	gpsd.sysconfig
Patch1:		gpsd-2.90-udev.patch
Patch2:		gpsd-2.95-fix-link.patch
Patch3:		gpsd-2.95-silentmake.patch
Patch4:		gpsd.ldflags.patch

BuildRequires:  docbook-style-xsl
BuildRequires:  udev
BuildRequires:	xmlto
BuildRequires:	lesstif-devel
BuildRequires:	qt4-devel
BuildRequires:	pkgconfig(bluez)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(ncurses)
BuildRequires:	pkgconfig(python)
Requires:	%{name}-python = %{version}-%{release}

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

%package -n	%{libgps}
Summary:	Libraries for gpsd
Group:		System/Libraries
Conflicts:	%{_lib}gpsd19 < 2.95-5

%description -n	%{libgps}
This package contains a shared library for %{name}.

%package -n	%{libname}
Summary:	Libraries for gpsd
Group:		System/Libraries
Obsoletes:	%{_lib}gpsd19 < 2.95-5

%description -n	%{libname}
This package contains a shared library for %{name}.

%package -n     %{libqtname}
Summary:        Qt bindings for gpsd
Group:          System/Libraries

%description -n %{libqtname}
This package contains Qt bindings for gpsd.

%package -n	%{devname}
Summary:	Client libraries in C and Python for talking to a running gpsd or GPS
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libgps} = %{version}
Requires:	%{libname} = %{version}
Requires:	%{libqtname} = %{version}
Obsoletes:	%{_lib}gpsd-static-devel < 2.95-5

%description -n	%{devname}
This package provides C header files for the gpsd shared libraries
that manage access to a GPS for applications; also Python modules.
You will need to have gpsd installed for it to work.

%package	clients
Summary:	Clients for gpsd with an X interface
Group:		Sciences/Geosciences
Requires:	%{name}
Requires:	%{name}-python

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
%apply_patches

%build
export LDFLAGS="$LDFLAGS -lbluetooth"
%configure2_5x \
	--disable-static \
	--enable-dbus \
	--enable-bluetooth

%make

%install
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
install -d -m 0755 %{buildroot}%{_sysconfdir}/init.d
install -p -m 0755 packaging/rpm/gpsd.init \
	%{buildroot}%{_sysconfdir}/init.d/gpsd

install -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0644 packaging/rpm/gpsd.sysconfig \
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

%files
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

%files -n %{libgps}
%{_libdir}/libgps.so.%{gpsmaj}*

%files -n %{libname}
%{_libdir}/libgpsd.so.%{major}*

%files -n %{libqtname}
%{_libdir}/libQgpsmm.so.%{gpsmaj}*

%files -n %{devname}
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

%files clients
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
%{py_platsitedir}/*

