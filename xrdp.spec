Summary:	Open source remote desktop protocol (RDP) server
Name:		xrdp
Version:	0.4.0
Release:	%mkrel 0.3
License:	GPL
Group:		System/Servers
URL:		http://xrdp.sourceforge.net/
Source0:	http://dl.sf.net/xrdp/xrdp-%{version}.tar.gz
Source1:	xrdp.init
Patch0:		xrdp-0.4.0-sesman.patch
Patch1:		xrdp-0.4.0-sesmantools.patch
Patch2:		xrdp-0.4.0-docs.patch
Patch3:		xrdp-optflags.diff
Patch4:		xrdp-no_rpath.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	pam-devel
BuildRequires:	openssl-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The goal of this project is to provide a fully functional Linux terminal
server, capable of accepting connections from rdesktop and Microsoft's own
terminal server / remote desktop clients.

%prep

%setup -q

%patch0
%patch1
%patch2
%patch3 -p1
%patch4 -p1


cp %{SOURCE1} xrdp.init

perl -pi -e 's|/lib\b|/%{_lib}|g' Makefile */Makefile
perl -pi -e "s|\@libexecdir\@|%{_libdir}/xrdp|g" xrdp.init

%build
%serverbuild
make

%install
rm -rf %{buildroot}

make installdeb DESTDIRDEB="%{buildroot}"

install -Dp -m0755 sesman/libscp/libscp.so %{buildroot}%{_libdir}/xrdp/libscp.so

install -d %{buildroot}%{_initrddir}
install -m0755 xrdp.init %{buildroot}%{_initrddir}/xrdp

# cleanup 
rm -rf %{buildroot}%{_sysconfdir}/init.d

%post
%_post_service xrdp

%preun
%_preun_service xrdp

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc COPYING *.txt instfiles/*.sh
%attr(0755,root,root) %{_initrddir}/xrdp
%dir %{_sysconfdir}/xrdp
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/xrdp/*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pam.d/sesman
%dir %{_libdir}/xrdp
%attr(0755,root,root) %{_libdir}/xrdp/*.so
%attr(0644,root,root) %{_libdir}/xrdp/ad256.bmp
%attr(0644,root,root) %{_libdir}/xrdp/cursor0.cur
%attr(0644,root,root) %{_libdir}/xrdp/cursor1.cur
%attr(0755,root,root) %{_libdir}/xrdp/sesman
%attr(0755,root,root) %{_libdir}/xrdp/startwm.sh
%attr(0644,root,root) %{_libdir}/xrdp/Tahoma-10.fv1
%attr(0755,root,root) %{_libdir}/xrdp/xrdp
%attr(0644,root,root) %{_libdir}/xrdp/xrdp256.bmp
%attr(0644,root,root) %{_mandir}/man5/*.5*
%attr(0644,root,root) %{_mandir}/man8/*.8*
