Summary:	Java application server JBoss
Summary(pl):	Serwer aplikacji Javy JBoss
Name:		jboss
Version:	3.2.5
Release:	1
License:	LGPL
Group:		Networking/Daemons/Java
Source0:	http://dl.sourceforge.net/jboss/%{name}-%{version}-src.tar.gz
# Source0-md5:	ded8ad667e49d82a4567d2c8f726fcbc
Source1:	http://dl.sourceforge.net/jboss/QuickStart-30x.pdf
# Source1-md5:	ca9f0c92510b230e91917793516ad814
Source2:	%{name}.init
Source3:	%{name}.conf
Patch0:		%{name}-jpackage.patch
Patch1:		%{name}-shutdown.patch
URL:		http://www.jboss.org/
BuildRequires:	jdk
BuildRequires:	rpmbuild(macros) >= 1.159
Requires:	jdk
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(post,preun):	/sbin/chkconfig
Provides:	group(jboss)
Provides:	user(jboss)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Java application server JBoss.

%description -l pl
Serwer aplikacji Javy JBoss.

%prep
%setup -q -n %{name}-%{version}-src
#%patch0 -p1
#%patch1 -p0

%build
JAVA_HOME=%{_libdir}/java
export JAVA_HOME
chmod +x build/build.sh
build/build.sh

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

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

install -d $RPM_BUILD_ROOT/etc/sysconfig
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

# ghost files and directories
install -d $RPM_BUILD_ROOT%{_libdir}/%{name}/tmp
install -d $RPM_BUILD_ROOT/var/lib/%{name}/{default,all,minimal}/{db,log,tmp}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid jboss`" ]; then
	if [ "`/usr/bin/getgid jboss`" != 100 ]; then
		echo "Error: group jboss doesn't have gid=100. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 100 jboss
fi
if [ -n "`/bin/id -u jboss 2>/dev/null`" ]; then
	if [ "`/bin/id -u jboss`" != 100 ]; then
		echo "Error: user jboss doesn't have uid=100. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 100 -g jboss -d %{_libdir}/%{name} -s /bin/sh \
		-c "JBoss" jboss
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
	%userremove jboss
	%groupremove jboss
fi

%files
%defattr(644,jboss,jboss,755)
%attr(754,root,root) /etc/rc.d/init.d/%{name}

%dir %{_libdir}/%{name}

%dir %{_libdir}/%{name}/bin
%attr(755,root,root) %{_libdir}/%{name}/bin/*.sh
%{_libdir}/%{name}/bin/*.jar

%{_libdir}/%{name}/client
%{_libdir}/%{name}/docs
%{_libdir}/%{name}/lib
%{_libdir}/%{name}/server

%dir /var/lib/%{name}
/var/lib/%{name}/default/conf
/var/lib/%{name}/default/deploy
/var/lib/%{name}/default/lib
/var/lib/%{name}/all/conf
/var/lib/%{name}/all/deploy
/var/lib/%{name}/all/lib
/var/lib/%{name}/minimal/conf
/var/lib/%{name}/minimal/deploy
/var/lib/%{name}/minimal/lib

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
