Summary:   Open source remote desktop protocol (RDP) server
Name:      xrdp
Epoch:     1
Version:   0.9.11
Release:   1
License:   ASL 2.0
Group:     Networking/Remote access
URL:       http://www.xrdp.org/
Source0:   https://github.com/neutrinolabs/xrdp/releases/download/v%{version}/xrdp-%{version}.tar.gz
Source1:   xrdp-sesman.pamd
Source2:   xrdp.sysconfig
Source3:   xrdp.logrotate
Source4:   openssl.conf
Patch0:    xrdp-0.9.9-sesman.patch
Patch1:    xrdp-0.9.9-xrdp-ini.patch
Patch2:    xrdp-0.9.4-service.patch
Patch3:    xrdp-0.9.2-setpriv.patch
Patch4:    xrdp-0.9.10-scripts-libexec.patch
Patch5:    xrdp-0.9.6-script-interpreter.patch
Patch6:    make-fix.patch

BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xfixes)
BuildRequires: pkgconfig(xrandr)
BuildRequires: openssl
BuildRequires: lame-devel
BuildRequires: pam-devel
BuildRequires: pkgconfig(libjpeg)
BuildRequires: pkgconfig(fuse)
BuildRequires: pkgconfig(openssl) >= 1.1
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(pixman-1)
BuildRequires: pkgconfig(systemd)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: nasm


# tigervnc-server-minimal provides Xvnc (default for now)
Requires: tigervnc-server
Requires: xinitrc
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(posttrans): openssl

%description
xrdp provides a fully functional RDP server compatible with a wide range
of RDP clients, including FreeRDP and Microsoft RDP client.

%package devel
Summary: Headers and pkg-config files needed to compile xrdp backends

%description devel
This package contains headers necessary for developing xrdp backends that
talk to xrdp.

%prep
%autosetup -p1

# create 'bash -l' based startwm, to pick up PATH etc.
echo '#!/bin/bash -l
. %{_libexecdir}/xrdp/startwm.sh' > sesman/startwm-bash.sh

%build

pushd librfxcodec
%configure \
   --disable-shared \
   --enable-static
%make_build
popd

pushd libpainter
%configure \
   --disable-shared \
   --enable-static
%make_build
popd

%configure     --enable-fuse \
               --enable-pixman \
	       --enable-rfxcodec \
               --enable-painter \
               --enable-ipv6 \
               --enable-mp3lame \
               --enable-opus \
               --enable-jpeg \
               --enable-tjpeg

%make_build

%install
%make_install

#remove .la and .a files
find %{buildroot} -name '*.a' -delete
find %{buildroot} -name '*.la' -delete

# remove libpainter devel files
rm -f %{buildroot}%{_includedir}/painter.h \
      %{buildroot}%{_libdir}/libpainter.* \
      %{buildroot}%{_libdir}/pkgconfig/libpainter.pc

# remove .so files for non-modules
rm -f %{buildroot}%{_libdir}/xrdp/libcommon.so \
       %{buildroot}%{_libdir}/xrdp/libscp.so \
       %{buildroot}%{_libdir}/xrdp/libxrdp.so \
       %{buildroot}%{_libdir}/xrdp/libxrdpapi.so \
       %{buildroot}%{_libdir}/librfxencode.so

#install sesman pam config /etc/pam.d/xrdp-sesman
%{__install} -Dp -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/xrdp-sesman

#install xrdp sysconfig /etc/sysconfig/xrdp
%{__install} -Dp -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/xrdp

#install logrotate /etc/logrotate.d/xrdp
%{__install} -Dp -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/xrdp

#install openssl.conf /etc/xrdp
%{__install} -Dp -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/xrdp/openssl.conf

#install 'bash -l' startwm script
%{__install} -Dp -m 755 sesman/startwm-bash.sh %{buildroot}%{_libexecdir}/xrdp/startwm-bash.sh

#move startwm and reconnectwm scripts to libexec
%{__mv} -f %{buildroot}%{_sysconfdir}/xrdp/startwm.sh %{buildroot}%{_libexecdir}/xrdp/
%{__mv} -f %{buildroot}%{_sysconfdir}/xrdp/reconnectwm.sh %{buildroot}%{_libexecdir}/xrdp/

%post
%_create_ssl_certificate %{name}
%_post_service %{name}

%preun
%_preun_service %{name}

%posttrans
if [ ! -s %{_sysconfdir}/xrdp/rsakeys.ini ]; then
  (umask 377; %{_bindir}/xrdp-keygen xrdp %{_sysconfdir}/xrdp/rsakeys.ini >/dev/null)
fi
chmod 400 %{_sysconfdir}/xrdp/rsakeys.ini

if [ ! -s %{_sysconfdir}/xrdp/cert.pem ]; then
  (umask 377; openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 3652 \
    -keyout %{_sysconfdir}/xrdp/key.pem \
    -out %{_sysconfdir}/xrdp/cert.pem \
    -config %{_sysconfdir}/xrdp/openssl.conf >/dev/null 2>&1)
fi
chmod 400 %{_sysconfdir}/xrdp/cert.pem
chmod 400 %{_sysconfdir}/xrdp/key.pem


%files
%doc COPYING *.txt
%dir %{_libdir}/xrdp
%dir %{_sysconfdir}/xrdp
%dir %{_sysconfdir}/xrdp/pulse
%dir %{_datadir}/xrdp
%dir %{_libexecdir}/xrdp
%config(noreplace) %{_sysconfdir}/xrdp/xrdp.ini
%config(noreplace) %{_sysconfdir}/pam.d/xrdp-sesman
%config(noreplace) %{_sysconfdir}/logrotate.d/xrdp
%config(noreplace) %{_sysconfdir}/sysconfig/xrdp
%config(noreplace) %{_sysconfdir}/xrdp/sesman.ini
%exclude %{_sysconfdir}/xrdp/xrdp.sh
%exclude %ghost %{_sysconfdir}/xrdp/*.pem
%exclude %ghost %{_sysconfdir}/xrdp/rsakeys.ini
%{_sysconfdir}/xrdp/km*.ini
%{_sysconfdir}/xrdp/openssl.conf
%{_sysconfdir}/xrdp/xrdp_keyboard.ini
%{_libexecdir}/xrdp/startwm*.sh
%{_libexecdir}/xrdp/reconnectwm.sh
%{_bindir}/xrdp-genkeymap
%{_bindir}/xrdp-sesadmin
%{_bindir}/xrdp-keygen
%{_bindir}/xrdp-sesrun
%{_bindir}/xrdp-dis
%{_sbindir}/xrdp-chansrv
%{_sbindir}/xrdp
%{_sbindir}/xrdp-sesman
%{_datadir}/xrdp/ad256.bmp
%{_datadir}/xrdp/cursor0.cur
%{_datadir}/xrdp/cursor1.cur
%{_datadir}/xrdp/xrdp256.bmp
%{_datadir}/xrdp/sans-10.fv1
%{_datadir}/xrdp/ad24b.bmp
%{_datadir}/xrdp/xrdp24b.bmp
%{_datadir}/xrdp/xrdp_logo.bmp
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_mandir}/man1/*
#% {_libdir}/lib*.so.*
%{_libdir}/xrdp/lib*.so.*
%{_libdir}/xrdp/libmc.so
%{_libdir}/xrdp/libvnc.so
%{_libdir}/xrdp/libxup.so
%{_sysconfdir}/xrdp/pulse/default.pa
%{_unitdir}/xrdp-sesman.service
%{_unitdir}/xrdp.service
%ghost %{_localstatedir}/log/xrdp.log
%ghost %{_localstatedir}/log/xrdp-sesman.log
%attr(0600,root,root) %verify(not size md5 mtime) %{_sysconfdir}/xrdp/rsakeys.ini

%files devel
%{_includedir}/xrdp*
%{_includedir}/rfxcodec_*.h
%{_libdir}/pkgconfig/xrdp.pc
%{_libdir}/pkgconfig/rfxcodec.pc
