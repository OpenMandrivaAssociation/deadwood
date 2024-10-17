#define debug_package %{nil}

Summary:	A fully recursive caching DNS resolver
Name:		deadwood
Version:	3.2.02
Release:	5
License:	BSD
Group:		System/Servers
URL:		https://www.maradns.org
Source0:	http://www.maradns.org/%{name}/stable/%{name}-%{version}.tar.bz2
Source1:	deadwood.service
Source2:	deadwood.tmpfiles.d
Requires(post,preun):	rpm-helper

%description
Deadwood is a fully recursive DNS cache. This is a DNS server with the 
following features:
 * Full support for both DNS recursion and DNS forwarding caching
 * Small size and memory footprint suitable for embedded systems
 * Simple and clean codebase
 * Secure design
 * Spoof protection: Strong cryptography used to determine the
 Query ID and source port
 * Ability to read and write the cache to a file
 * Dynamic cache that deletes entries not recently used
 * Ability to use expired entries in the cache when it is
 impossible to contact upstream DNS servers.
 * Both DNS-over-UDP and DNS-over-TCP are handled by the same daemon
 * Built-in dnswall functionality

%prep
%setup -q

%build
export FLAGS="%{optflags} -DIPV6"
cd src
%make
cd ../tools
%make

%install
mkdir -p %{buildroot}%{_sbindir}
install src/Deadwood %{buildroot}%{_sbindir}/deadwood
install tools/duende %{buildroot}%{_sbindir}/duende
mkdir -p %{buildroot}%{_mandir}/man1
install doc/*.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_sysconfdir}/maradns/logger
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_unitdir}
install %{SOURCE1} %{buildroot}%{_unitdir}/deadwood.service
install doc/dwood3rc %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_logdir}/%{name}

install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_tmpfilesdir}/%{name}.conf
%pre
%_pre_useradd %{name} /etc/%{name} /bin/false
%_pre_groupadd %{name} %{name}

%post
%tmpfiles_create
%systemd_post %{name}.service
cat << EOF
Please update the maradns_uid and maradns_gid otions in %{_sysconfdir}/dwood3c (line `%__grep -n '^maradns_uid' %{_sysconfdir}/dwood3rc | %__sed 's/:.*$//'`)
to the valid deadwood uid (`%__grep '^deadwood:' /etc/passwd | %__awk -F ':' '{print $3}'`) and gid (`%__grep '^deadwood:' /etc/passwd | %__awk -F ':' '{print $4}'`)

%preun
%systemd_preun %{name}.service

%postun
%_postun_userdel %{name}
%_postun_groupdel %{name}
%systemd_postun_with_restart %{name}.service

%files
%doc doc/*
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/maradns/logger
%attr(750,root,root) %{_unitdir}/%{name}*
%config(noreplace) %{_sysconfdir}/dwood3rc
%{_sbindir}/deadwood
%{_sbindir}/duende
%{_mandir}/man1/*
%{_tmpfilesdir}/*
%dir %{_logdir}/%{name}
