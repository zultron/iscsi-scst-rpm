# use --define "kernel X.Y.Z" to build for different kernel 
# use --target i686 on i386
%{!?kernel:%define kernel %(rpm -q kernel-source kernel-devel --qf "%{RPMTAG_VERSION}-%{RPMTAG_RELEASE}\\n" | tail -1)}

Summary: iSCSI SCST target kernel driver
Name: iscsi-scst
Version: 1.0.1.1
Release: 4.cern
License: GPL
Buildroot: %{_tmppath}/%{name}-buildroot
Group: Applications/File
Source: %{name}-%{version}.tar.gz
Packager: Andras.Horvath@cern.ch
URL: http://scst.sourceforge.net/
BuildRequires: scst-kernel-headers >= 1.0.1.1

Source1: iscsi-scst.init.script

%description
This driver is a forked with all respects version of iSCSI Enterprise
Target (IET) (http://iscsitarget.sourceforge.net/) with updates to work
over SCST as well as with many improvements and bugfixes (see ChangeLog
file). The reason of fork is that the necessary changes are intrusive
and with the current IET merge policy, where only simple bugfix-like
patches, which doesn't touch the core code, could be merged, it is very
unlikely that they will be merged in the main IET trunk.


%package target-utils
Summary: iSCSI SCST target daemon and utility programs
Group: Applications/File
# I think it does ? 
Requires: kernel-module-%{name}
Obsoletes: iscsi-scst-utils

%description target-utils
This driver is a forked with all respects version of iSCSI Enterprise
Target (IET) (http://iscsitarget.sourceforge.net/) with updates to work
over SCST as well as with many improvements and bugfixes (see ChangeLog
file). The reason of fork is that the necessary changes are intrusive
and with the current IET merge policy, where only simple bugfix-like
patches, which doesn't touch the core code, could be merged, it is very
unlikely that they will be merged in the main IET trunk.

%package -n kernel-module-%{name}-%{kernel}
Summary: iSCSI SCST target driver, kernel modules
Group: System Environment/Kernel
Requires: kernel-%{_target_cpu} = %{kernel}
# well, the 'or greater' below may not be necessarily true ...
Requires: kernel-module-scst-%{kernel} >= 1.0.1.1
BuildRequires: kernel-devel = %{kernel}
Provides: kernel-module
Provides: kernel-module-%{name} = %{version}-%{release}
ExclusiveArch: i686 x86_64 ia64

%description -n kernel-module-%{name}-%{kernel}
This driver is a forked with all respects version of iSCSI Enterprise
Target (IET) (http://iscsitarget.sourceforge.net/) with updates to work
over SCST as well as with many improvements and bugfixes (see ChangeLog
file). The reason of fork is that the necessary changes are intrusive
and with the current IET merge policy, where only simple bugfix-like
patches, which doesn't touch the core code, could be merged, it is very
unlikely that they will be merged in the main IET trunk.

These modules were built for kernel %{kernel} on architecture %{arch}

%prep
%setup
perl -p -i -e 's,/sbin/depmod,:,g' Makefile

%build

make DESTDIR=%{buildroot} SCST_INC_DIR=/usr/include/scst SBINDIR=/usr/sbin KVER=%{kernel}

%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} SCST_INC_DIR=/usr/include/scst SBINDIR=/usr/sbin KVER=%{kernel}
mkdir -p %{buildroot}/usr/share/doc/%{name}-%{version}-target-utils
cp doc/iscsi-scst-howto.txt README ChangeLog* COPYING AskingQuestions ToDo %{buildroot}/usr/share/doc/%{name}-%{version}-target-utils
mkdir -p %{buildroot}/usr/share/man/man{5,8}
cp doc/manpages/*.8 %{buildroot}/usr/share/man/man8
cp doc/manpages/*.5 %{buildroot}/usr/share/man/man5
# no we do want docs in modules (since it will clash with docs elsewhere ..)
#cp README ChangeLog COPYING AskingQuestions ToDo %{buildroot}/usr/share/doc/%{name}-%{version}-modules

# yes, I do not like included init script (and besides .. it won;t work)
cp -f %{SOURCE1} %{buildroot}/etc/init.d/iscsi-scst
chmod 755 %{buildroot}/etc/init.d/iscsi-scst
# ok, no idea what should be in it ;-)
touch %{buildroot}/etc/iscsi-scst.conf
chmod 644 %{buildroot}/etc/iscsi-scst.conf

%clean
rm -rf %{buildroot}

%files target-utils
%defattr(-,root,root)
/usr/sbin/iscsi-scst-adm
/usr/sbin/iscsi-scstd
/etc/init.d/iscsi-scst
%config(noreplace) /etc/iscsi-scst.conf
%doc /usr/share/doc
%doc /usr/share/man

%doc /usr/share/doc/%{name}-%{version}-target-utils

%files -n kernel-module-%{name}-%{kernel}
%defattr(-,root,root)
/lib/modules/%{kernel}/extra/iscsi-scst.ko
#doc /usr/share/doc/%{name}-%{version}-modules

%post -n kernel-module-%{name}-%{kernel}
/sbin/depmod -aeF /boot/System.map-%{kernel} %{kernel} > /dev/null || :
# if we would need this in initrd we could add:
#/sbin/mkinitrd --allow-missing -f /boot/initrd-%{kernel}.img %{kernel} > /dev/null || :

%postun -n kernel-module-%{name}-%{kernel}
/sbin/depmod -aeF /boot/System.map-%{kernel} %{kernel} > /dev/null || :
# if we would need this in initrd we could add:
#/sbin/mkinitrd --allow-missing -f /boot/initrd-%{kernel}.img %{kernel} > /dev/null || :


%post target-utils
/sbin/chkconfig --add iscsi-scst || :

%preun target-utils
if [ "$1" = "0" ]; then
        /sbin/service iscsi-scst stop > /dev/null 2>&1
        /sbin/chkconfig --del iscsi-scst
fi
exit 0

%postun target-utils
if [ "$1" -ge "1" ]; then
        /sbin/service iscsi-scst condrestart > /dev/null 2>&1
fi
exit 0



%changelog
* Mon Nov 23 2009  Jaroslaw Polok <jaroslaw.polok@cern.ch> 1.0.11-4.cern
- renamed iscsi-scst-utils package to iscsi-scst-target-utils for more
  consistency with other iscsi packages (scsi-target-utils)

* Fri Nov 20 2009  Andras HORVATH <andras.horvath@cern.ch> 1.0.11-3.cern
- added manpages and howto

* Mon Nov 16 2009  Jaroslaw Polok <jaroslaw.polok@cern.ch> 1.0.11-2.cern
- 2nd attempt at packaging ;-)

* Fri Nov 13 2009  Andras HORVATH <andras.horvath@cern.ch> 1.0.11-1.cern
- first packaging attempt
