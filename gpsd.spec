%define _hotplugdir %{_prefix}/lib/hotplug

%define _disable_rebuild_configure 1
%define _disable_ld_no_undefined 1

%define gpsmaj 29
%define major 29
%define libname %mklibname gps
%define libqtname %mklibname Qgpsmm
%define oldlibname %mklibname gps %{gpsmaj}
%define oldlibqtname %mklibname Qgpsmm %{gpsmaj}
%define devname %mklibname %{name} -d

%bcond_without qt
%ifarch riscv64
%bcond_with gtk
%else
%bcond_without gtk
%endif

Summary:	GPS data translator and GUI
Name:		gpsd
Version:	3.24
Release:	2
License:	BSD
Group:		Sciences/Geosciences
Url:		http://catb.org/gpsd/
Source0:	http://download.savannah.gnu.org/releases/gpsd/gpsd-%{version}.tar.gz
Source1:	gpsd.rules
Source2:	gpsd.sysconfig
Patch1:		gpsd-2.90-udev.patch

BuildRequires:	docbook-style-xsl
BuildRequires:	udev
BuildRequires:	xmlto
BuildRequires:	scons
%if %{with qt}
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5Network)
BuildRequires:	pkgconfig(Qt5Widgets)
%endif
%if %{with gtk}
BuildRequires:	python-serial
BuildRequires:	python-cairo
BuildRequires:	python-gi
BuildRequires:	pkgconfig(gtk+-3.0)
%endif
BuildRequires:	pkgconfig(bluez)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	pkgconfig(python3)
BuildRequires:	systemd-rpm-macros
Requires:	%{name}-python >= %{EVRD}
Requires:	%{libname} >= %{EVRD}
%{?systemd_requires}

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

%package -n %{libname}
Summary:	Libraries for gpsd
Group:		System/Libraries
Conflicts:	%{_lib}gpsd19 < 2.95-5
%rename %{oldlibname}

%description -n %{libname}
This package contains a shared library for %{name}.

%if %{with qt}
%package -n %{libqtname}
Summary:	Qt bindings for gpsd
Group:		System/Libraries
%rename %{oldlibqtname}

%description -n %{libqtname}
This package contains Qt bindings for gpsd.
%endif

%package -n %{devname}
Summary:	Client libraries in C and Python for talking to a running gpsd or GPS
Group:		Development/C
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
%if %{with qt}
Requires:	%{libqtname} = %{EVRD}
%endif
Obsoletes:	%{_lib}gpsd-static-devel < 2.95-5

%description -n %{devname}
This package provides C header files for the gpsd shared libraries
that manage access to a GPS for applications; also Python modules.
You will need to have gpsd installed for it to work.

%package clients
Summary:	Clients for gpsd with an X interface
Group:		Sciences/Geosciences
Requires:	%{name}
Requires:	%{name}-python

%description clients
xgps is a simple test client for gpsd with an X interface. It displays
current GPS position/time/velocity information and (for GPSes that
support the feature) the locations of accessible satellites.

xgpsspeed is a speedometer that uses position information from the GPS.
It accepts an -h option and optional argument as for gps, or a -v option
to dump the package version and exit. Additionally, it accepts -rv
(reverse video) and -nc (needle color) options.

%package python
Summary:	Python bindings for gpsd
Group:		Development/Python
Requires:	%{libname} = %{EVRD}

%description python
This package contains the Python bindings for gpsd. It will be needed
for any applications that interface with gpsd via python.

%prep
%autosetup -p1
sed -i 's/ncurses5-config/ncurses6-config/' SConstruct
sed -i 's/ncursesw5-config/ncursesw6-config/' SConstruct
# fix paths in systemd unit files
sed -i 's|/usr/local/sbin|%{_sbindir}|' systemd/*.service.in
# fix systemd path
sed -i 's|systemd_dir =.*|systemd_dir = '\'%{_unitdir}\''|' SConstruct
# don't try reloading systemd when installing in the build root
sed -i 's|systemctl daemon-reload|true|' SConstruct
# don't set RPATH
sed -i 's|env.Prepend.*RPATH.*|pass #\0|' SConstruct

%build
%set_build_flags
%scons \
	prefix=%{_prefix} \
	execprefix=%{_exec_prefix} \
	sbindir=%{_sbindir} \
	datadir=%{_datadir} \
	libdir=%{_libdir} \
	rundir=%{_rundir} \
	unitdir=%{_unitdir} \
	udevdir=$(dirname %{_udevrulesdir}) \
	target_python=python3 \
	python_libdir=%{py3_puresitedir} \
%if %{without qt}
	qt=no \
%endif
	systemd=yes \
	qt_versioned=5 \
	dbus_export=yes

%if 0
# Currently fails
%check
export CC=%{__cc}
export CXX=%{__cxx}
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LD_LIBRARY_PATH=$(pwd):$LD_LIBRARY_PATH
scons check
%endif

%install
%set_build_flags
export CC=%{__cc}
export CXX=%{__cxx}
export DESTDIR=%{buildroot}
# Setting sysroot to anything at all disables running
# systemctl daemon-reload during "make install". But we
# can't just replace DESTDIR with sysroot because scons
# is "smart" enough to realize changed sysroot == changed
# headers --> tries to rebuild and screams about not
# finding headers in the "sysroot".
STRIP=/bin/true %scons_install systemd_install udev-install sysroot=/

# udev rules
install -d -m 0755 %{buildroot}%{_sysconfdir}/udev/rules.d
install -p -m 0644 gpsd-%{version}/gpsd.rules %{buildroot}%{_sysconfdir}/udev/rules.d/70-gpsd.rules

install -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/gpsd

mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d
install -m644 %{SOURCE1} %{buildroot}%{_sysconfdir}/udev/rules.d/70-gpsd.rules

mkdir -p %{buildroot}%{_sysconfdir}/udev/agents.d/usb
install -m755 gpsd.hotplug %{buildroot}%{_sysconfdir}/udev/agents.d/usb/gpsd

# Install the .desktop files
desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    packaging/X11/xgps.desktop
desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    packaging/X11/xgpsspeed.desktop

# Install logo icon for .desktop files
%{__install} -d -m 0755 %{buildroot}%{_datadir}/gpsd
%{__install} -p -m 0644 packaging/X11/gpsd-logo.png %{buildroot}%{_datadir}/gpsd/gpsd-logo.png

# Missed in scons install
%{__install} -p -m 0755 gpsinit %{buildroot}%{_sbindir}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable gpsd.socket
EOF

%post
%systemd_post %{name}.socket

%preun
%systemd_preun %{name}.socket

%postun
%systemd_postun_with_restart %{name}.socket

%files
%{_sbindir}/gpsd
%{_sbindir}/gpsdctl
%{_sbindir}/gpsinit
%{_bindir}/gegps
%{_bindir}/gpsrinex
%{_bindir}/gps2udp
%{_bindir}/gpscat
%{_bindir}/gpsctl
%{_bindir}/gpsprof
%{_bindir}/gpsmon
%{_bindir}/gpsdecode
%{_bindir}/ntpshmmon
%{_bindir}/ubxtool
%{_bindir}/zerk
%{_mandir}/man1/ntpshmmon.1.*
%{_mandir}/man8/gpsd.8*
%{_mandir}/man8/gpsdctl.8*
%{_mandir}/man8/gpsinit.8*
%{_mandir}/man1/gegps.1*
%{_mandir}/man1/gps.1*
%{_mandir}/man1/gps2udp.1*
%{_mandir}/man1/gpsprof.1*
%{_mandir}/man1/gpscat.1*
%{_mandir}/man1/gpsctl.1*
%{_mandir}/man1/gpsrinex.1.zst
%{_mandir}/man1/ubxtool.1.zst
%{_mandir}/man1/zerk.1.zst
%{_mandir}/man1/gpsmon.1*
%{_mandir}/man1/gpsdecode.1*
%{_mandir}/man5/gpsd_json.5*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_sysconfdir}/udev/agents.d/usb/gpsd
%{_sysconfdir}/udev/rules.d/*.rules
%{_udevrulesdir}/*.rules
%{_presetdir}/86-%{name}.preset
%{_unitdir}/gpsd.service
%{_unitdir}/gpsd.socket
%{_unitdir}/gpsdctl@.service
%dir %{_datadir}/gpsd
%{_datadir}/gpsd/icons
%doc %{_datadir}/gpsd/doc

%libpackage gpsdpacket %{major}

%files -n %{libname}
%{_libdir}/libgps.so.%{gpsmaj}*

%if %{with qt}
%files -n %{libqtname}
%{_libdir}/libQgpsmm.so.%{gpsmaj}*
%endif

%files -n %{devname}
%doc TODO
%{_includedir}/gps.h
%{_includedir}/libgpsmm.h
%{_libdir}/libgps.so
%{_libdir}/libgpsdpacket.so
%if %{with qt}
%{_libdir}/libQgpsmm.so
%{_libdir}/libQgpsmm.prl
%{_mandir}/man3/libQgpsmm.3*
%endif
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man1/gpsfake.1*
%{_mandir}/man3/libgps.3*
%{_mandir}/man3/libgpsmm.3*
%{_bindir}/gpsfake

%files clients
%if %{with gtk}
%{_bindir}/xgps
%{_bindir}/xgpsspeed
%{_mandir}/man1/xgps.1*
%{_mandir}/man1/xgpsspeed.1*
%endif
%{_bindir}/cgps
%{_bindir}/gpscsv
%{_bindir}/gpsdebuginfo
%{_bindir}/gpsplot
%{_bindir}/gpssnmp
%{_bindir}/gpssubframe
%{_bindir}/gpspipe
%{_bindir}/gpxlogger
%{_bindir}/ppscheck
%{_bindir}/lcdgps
%{_mandir}/man1/cgps.1*
%{_mandir}/man1/gpscsv.1*
%{_mandir}/man1/gpsdebuginfo.1*
%{_mandir}/man1/gpsplot.1*
%{_mandir}/man1/gpssnmp.1*
%{_mandir}/man1/gpssubframe.1*
%{_mandir}/man1/gpspipe.1*
%{_mandir}/man1/lcdgps.1.*
%{_mandir}/man1/gpxlogger.1*
%{_mandir}/man8/ppscheck.8*
%{_datadir}/applications/*.desktop
%dir %{_datadir}/gpsd
%{_datadir}/gpsd/gpsd-logo.png

%files python
%{py3_puresitedir}/*
