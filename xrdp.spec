%define major 0
%define libname %mklibname %{name} %{major}

Summary:	Open source remote desktop protocol (RDP) server
Name:		xrdp
Version:	0.4.1
Release:	%mkrel 5
License:	GPL
Group:		System/Servers
URL:		http://xrdp.sourceforge.net/
Source0:	http://dl.sf.net/xrdp/xrdp-%{version}.tar.gz
Source1:	xrdp.init
Source2:	xrdp.logrotate
Source3:	xrdp.sysconfig
Patch0:		xrdp-0.4.0-sesman.patch
Patch1:		xrdp-0.4.0-sesmantools.patch
Patch2:		xrdp-0.4.0-docs.patch
Patch3:		xrdp-optflags.diff
Patch4:		xrdp-no_rpath.diff
Patch5:		xrdp-mdv_conf.diff
Patch6:		xrdp-window_managers.diff
Patch7:		xrdp-0.4.0-mdv_libifictions.diff
Patch8:		xrdp-0.4.1-wformat_fix.diff
Patch9:		xrdp-0.4.1-fix-link.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	pam-devel
BuildRequires:	openssl-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The goal of this project is to provide a fully functional Linux terminal
server, capable of accepting connections from rdesktop and Microsoft's own
terminal server / remote desktop clients.

%package -n	%{libname}
Summary:	Shared libraries and plugins for xrdp
Group: 		System/Libraries

%description -n	%{libname}
The goal of this project is to provide a fully functional Linux terminal
server, capable of accepting connections from rdesktop and Microsoft's own
terminal server / remote desktop clients.

This package contains the shared libraries and plugins for xrdp.

%prep
%setup -q
%patch0
%patch1
%patch2
%patch3 -p1
%patch4 -p1
%patch5 -p0
%patch6 -p0
%patch7 -p1
%patch8 -p0
%patch9 -p0 -b .link

cp %{SOURCE1} xrdp.init
cp %{SOURCE2} xrdp.logrotate
cp %{SOURCE3} xrdp.sysconfig

perl -pi -e 's|/lib\b|/%{_lib}|g' Makefile */Makefile
perl -pi -e "s|\@libexecdir\@|%{_libdir}/xrdp|g" xrdp.init

%build
%serverbuild
make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/xrdp
install -d %{buildroot}%{_sysconfdir}/pam.d
install -d %{buildroot}/var/log/xrdp
install -d %{buildroot}%{_libdir}/xrdp
install -d %{buildroot}%{_mandir}/man5
install -d %{buildroot}%{_mandir}/man8

install -m0755 rdp/librdp.so.%{major} %{buildroot}%{_libdir}/
install -m0755 vnc/libvnc.so.%{major} %{buildroot}%{_libdir}/
install -m0755 xup/libxup.so.%{major} %{buildroot}%{_libdir}/
install -m0755 libxrdp/libxrdp.so.%{major} %{buildroot}%{_libdir}/
install -m0755 sesman/libscp/libscp.so.%{major} %{buildroot}%{_libdir}/

install -m0755 sesman/sesman %{buildroot}%{_sbindir}/
install -m0755 sesman/sessvc %{buildroot}%{_sbindir}/
install -m0755 sesman/startwm.sh %{buildroot}%{_sbindir}/xrdp-startwm
install -m0755 sesman/tools/sesrun %{buildroot}%{_sbindir}/
install -m0755 sesman/tools/sestest %{buildroot}%{_sbindir}/
install -m0644 sesman/sesman.ini %{buildroot}%{_sysconfdir}/xrdp/

install -m0755 xrdp/xrdp %{buildroot}%{_sbindir}/
install -m0644 xrdp/ad256.bmp %{buildroot}%{_libdir}/xrdp/
install -m0644 xrdp/xrdp256.bmp %{buildroot}%{_libdir}/xrdp/
install -m0644 xrdp/cursor0.cur %{buildroot}%{_libdir}/xrdp/
install -m0644 xrdp/cursor1.cur %{buildroot}%{_libdir}/xrdp/
install -m0644 xrdp/Tahoma-10.fv1 %{buildroot}%{_libdir}/xrdp/
install -m0644 xrdp/xrdp.ini %{buildroot}%{_sysconfdir}/xrdp/
install -m0644 xrdp/rsakeys.ini %{buildroot}%{_sysconfdir}/xrdp/

install -m0644 instfiles/pam.d/sesman %{buildroot}%{_sysconfdir}/pam.d/
install -m0644 docs/man/*.5 %{buildroot}%{_mandir}/man5/
install -m0644 docs/man/*.5 %{buildroot}%{_mandir}/man8/

install -m0755 xrdp.init %{buildroot}%{_initrddir}/xrdp

install -m0644 xrdp.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/xrdp
touch %{buildroot}/var/log/xrdp/sesman.log
install -m0644 xrdp.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/xrdp

# cleanup 
rm -rf %{buildroot}%{_sysconfdir}/init.d

%post
if [ $1 = 1 ]; then
    %create_ghostfile /var/log/xrdp/sesman.log root root 644
fi

%_post_service xrdp

%preun
%_preun_service xrdp

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root,-)
%attr(0755,root,root) %{_libdir}/lib*.so.%{major}*

%files
%defattr(-,root,root)
%doc COPYING *.txt
%attr(0755,root,root) %{_initrddir}/xrdp
%dir %{_sysconfdir}/xrdp
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/xrdp/*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pam.d/sesman
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/xrdp
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/xrdp
%attr(0755,root,root) %{_sbindir}/sesman
%attr(0755,root,root) %{_sbindir}/sesrun
%attr(0755,root,root) %{_sbindir}/sessvc
%attr(0755,root,root) %{_sbindir}/sestest
%attr(0755,root,root) %{_sbindir}/xrdp
%attr(0755,root,root) %{_sbindir}/xrdp-startwm
%dir %{_libdir}/xrdp
%attr(0644,root,root) %{_libdir}/xrdp/ad256.bmp
%attr(0644,root,root) %{_libdir}/xrdp/cursor0.cur
%attr(0644,root,root) %{_libdir}/xrdp/cursor1.cur
%attr(0644,root,root) %{_libdir}/xrdp/Tahoma-10.fv1
%attr(0644,root,root) %{_libdir}/xrdp/xrdp256.bmp
%dir /var/log/xrdp
%ghost /var/log/xrdp/sesman.log
%attr(0644,root,root) %{_mandir}/man5/*
%attr(0644,root,root) %{_mandir}/man8/*
