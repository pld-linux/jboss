Summary:	JBoss
Summary(pl):	JBoss
Name:		jboss
Version:	3.0.6
Release:	1
License:	LGPL
Group:		Networking/Daemons/Java
Source0:	http://belnet.dl.sourceforge.net/sourceforge/%{name}/%{name}-%{version}-src.tgz
Source1:	http://belnet.dl.sourceforge.net/sourceforge/%{name}/QuickStart-30x.pdf
Source2:	%{name}.init
Source3:	%{name}.conf
Patch0:		%{name}-jpackage.patch
Patch1:		%{name}-shutdown.patch
URL:		http://www.jboss.org
BuildRequires:	java-env
BuildRequires:	jdk
Requires:	java-env
Requires:	jdk
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		javacfgdir	/etc/sysconfig/java

%description
JBoss

%prep
%setup -q -n %{name}-%{version}-src
%patch0 -p1
%patch1 -p0

%build
JAVA_HOME=%{_libdir}/java
export JAVA_HOME
build/build.sh

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
cp %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/%{name}/bin
install build/output/%{name}-%{version}/bin/*.jar $RPM_BUILD_ROOT%{_libdir}/%{name}/bin
install build/output/%{name}-%{version}/bin/{run.sh,shutdown.sh} $RPM_BUILD_ROOT%{_libdir}/%{name}/bin
cp -a build/output/%{name}-%{version}/client $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a build/output/%{name}-%{version}/docs $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a build/output/%{name}-%{version}/lib $RPM_BUILD_ROOT%{_libdir}/%{name}

install -d $RPM_BUILD_ROOT/var/lib/%{name}
cp -a build/output/%{name}-%{version}/server/all $RPM_BUILD_ROOT/var/lib/%{name}
cp -a build/output/%{name}-%{version}/server/default $RPM_BUILD_ROOT/var/lib/%{name}
cp -a build/output/%{name}-%{version}/server/minimal $RPM_BUILD_ROOT/var/lib/%{name}
ln -sf /var/lib/%{name} $RPM_BUILD_ROOT%{_libdir}/%{name}/server

# link */lib/*.jar to all/lib/*.jar if file already exists there
for SERV in minimal default
do
    FILES=`ls $RPM_BUILD_ROOT/var/lib/%{name}/$SERV/lib`
    for FILE in $FILES
    do
        if [ -f "$RPM_BUILD_ROOT/var/lib/%{name}/all/lib/$FILE" ]; then
	    ln -sf /var/lib/%{name}/all/lib/$FILE \
		$RPM_BUILD_ROOT/var/lib/%{name}/$SERV/lib/$FILE
	fi
    done
done

install -d $RPM_BUILD_ROOT%{javacfgdir}
javacpmgr --findjars $RPM_BUILD_ROOT > $RPM_BUILD_ROOT%{javacfgdir}/cp.%{name}

install -d $RPM_BUILD_ROOT/etc/sysconfig
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -z "`getgid %{name}`" ]; then
	/usr/sbin/groupadd -g 100 -r %{name} 2> /dev/null || true
fi

if [ -z "`id -u %{name} 2>/dev/null`" ]; then
	/usr/sbin/useradd -u 100 -g %{name} -M -r -d %{_libdir}/%{name} -s /bin/sh \
		-c "JBoss" %{name} 2> /dev/null || true
fi

%post
if [ "$1" = "1" ] ; then
	/sbin/chkconfig --add jboss
fi

%preun
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/jboss ]; then
		/etc/rc.d/init.d/jboss stop 1>&2
	fi
	/sbin/chkconfig --del jboss
fi

%postun
if [ "$1" = "0" ] ; then
	/usr/sbin/userdel jboss 2> /dev/null || true
	/usr/sbin/groupdel jboss 2> /dev/null || true
fi

%files
%defattr(644,jboss,jboss,755)
%attr(755,root,root) /etc/rc.d/init.d/%{name}

%dir %{_libdir}/%{name}

%dir %{_libdir}/%{name}/bin
%attr(755,root,root) %{_libdir}/%{name}/bin/*.sh
%{_libdir}/%{name}/bin/*.jar

%{_libdir}/%{name}/client
%{_libdir}/%{name}/docs
%{_libdir}/%{name}/lib
%{_libdir}/%{name}/server
/var/lib/%{name}

%attr(644,root,root) %config(noreplace) %verify(not size mtime md5) %{javacfgdir}/cp.*
%attr(644,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/%{name}

# ghost files and directories
%ghost %{_libdir}/%{name}/tmp
%ghost /var/lib/%{name}/default/db
%ghost /var/lib/%{name}/default/log
%ghost /var/lib/%{name}/default/tmp
%ghost /var/lib/%{name}/all/db
%ghost /var/lib/%{name}/all/log
%ghost /var/lib/%{name}/all/tmp
%ghost /var/lib/%{name}/minimal/db
%ghost /var/lib/%{name}/minimal/log
%ghost /var/lib/%{name}/minimal/tmp
