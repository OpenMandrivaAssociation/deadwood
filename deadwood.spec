Summary:	A fully recursive caching DNS resolver
Name:		deadwood
Version:	3.0.02
Release:	%mkrel 1
License:	BSD
Group:		System/Servers
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:		http://www.maradns.org
Source0:	http://www.maradns.org/%{name}/stable/%{name}-%{version}.tar.bz2
Source1:	deadwood.init
Requires(post):	rpm-helper

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
export FLAGS="$RPM_OPT_FLAGS -DIPV6"
cd src
%make
cd ../tools
%make

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_sbindir}
install src/Deadwood %{buildroot}/%{_sbindir}/deadwood
install tools/duende %{buildroot}/%{_sbindir}/duende
mkdir -p %{buildroot}%{_mandir}/man1
install doc/*.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}/%{_sysconfdir}/maradns/logger
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/%{_initrddir}
install %{SOURCE1} %{buildroot}/%{_initrddir}/deadwood
install doc/dwood3rc %{buildroot}/%{_sysconfdir}
mkdir -p %{buildroot}%{_logdir}/%{name}

%clean
rm -rf %{buildroot}/

%pre
%_pre_useradd %{name} /etc/%{name} /bin/false
%_pre_groupadd %{name} %{name}
#if [ $1 = 1 ]
#	then
#	/usr/sbin/groupadd -r -g 99 maradns > /dev/null 2>&1
#	/usr/sbin/useradd -u 99 -r -d /etc/maradns -s /bin/false \
#	-c "Maradns pseudo user" -g maradns maradns  > /dev/null 2>&1
#fi

%post
%_post_service %{name}
cat << EOF
Please update the maradns_uid and maradns_gid otions in %{_sysconfdir}/dwood3c (line `%__grep -n '^maradns_uid' %{_sysconfdir}/dwood3rc | %__sed 's/:.*$//'`)
to the valid deadwood uid (`%__grep '^deadwood:' /etc/passwd | %__awk -F ':' '{print $3}'`) and gid (`%__grep '^deadwood:' /etc/passwd | %__awk -F ':' '{print $4}'`)

%preun
%_preun_service %{name}

%postun
%_postun_userdel %{name}
%_postun_groupdel %{name}


%files
%defattr(-,root,root)
%doc doc/*
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/%{name}
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/maradns/logger
%attr(750,root,root) %{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/dwood3rc
%{_sbindir}/deadwood
%{_sbindir}/duende
%{_mandir}/man1/*
%dir %{_logdir}/%{name}
