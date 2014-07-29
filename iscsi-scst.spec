# use --define "kver X.Y.Z" to build for different kernel 
%{!?kernel:%define kver %(rpm -q kernel-devel --qf \\\
    "%{RPMTAG_VERSION}-%{RPMTAG_RELEASE}\\n" | tail -1)}
%global kmod_install_dir /lib/modules/%{kver}.%{_target_cpu}

# Minimum scst version to depend on
%global scst_version 2.0.0

# kernel source directory
%global kdir %{_usrsrc}/kernels/%{kver}.%{_target_cpu}

# SCST module symbols file
%global scst_module_symvers %{kdir}/scst/Module.symvers


Summary: iSCSI SCST target kernel driver
Name: iscsi-scst
Version: 2.2.1
Release: 0
License: GPL
Buildroot: %{_tmppath}/%{name}-buildroot
Group: Applications/File
URL: http://scst.sourceforge.net/
BuildRequires: scst-devel >= %{scst_version}
BuildRequires: kmod-scst-devel
%define tarball %{name}/%{name}-%{version}.tar.bz2
Source0: http://sourceforge.net/projects/scst/files/%{tarball}
Source1: %{name}.init.script


%description
ISCSI-SCST is a deeply reworked fork of iSCSI Enterprise Target (IET)
(http://iscsitarget.sourceforge.net). Reasons of the fork were:

 - To be able to use full power of SCST core.
 - To fix all the problems, corner cases issues and iSCSI standard
   violations which IET has.

See for more info http://iscsi-scst.sourceforge.net.


%package target-utils
Summary: iSCSI SCST target daemon and utility programs
Group: Applications/File


%description target-utils
This driver is a forked with all respects version of iSCSI Enterprise
Target (IET) (http://iscsitarget.sourceforge.net/) with updates to work
over SCST as well as with many improvements and bugfixes (see ChangeLog
file). The reason of fork is that the necessary changes are intrusive
and with the current IET merge policy, where only simple bugfix-like
patches, which doesn't touch the core code, could be merged, it is very
unlikely that they will be merged in the main IET trunk.


%package -n kmod-%{name}-%{kver}
Summary: iSCSI SCST target driver, kernel modules
Group: System Environment/Kernel
Requires: kernel-%{_target_cpu} = %{kver}
Requires: kmod-scst-%{kver}
Provides: kmod-%{name} = %{version}-%{release}


%description -n kmod-%{name}-%{kver}
This driver is a forked with all respects version of iSCSI Enterprise
Target (IET) (http://iscsitarget.sourceforge.net/) with updates to work
over SCST as well as with many improvements and bugfixes (see ChangeLog
file). The reason of fork is that the necessary changes are intrusive
and with the current IET merge policy, where only simple bugfix-like
patches, which doesn't touch the core code, could be merged, it is very
unlikely that they will be merged in the main IET trunk.

These modules were built for kernel %{kver}


%prep
%setup -q


%build
make DESTDIR=%{buildroot} SCST_INC_DIR=/usr/include/scst SBINDIR=/usr/sbin \
    KVER=%{kver}.%{_target_cpu} \
    KDIR=%{_usrsrc}/kernels/%{kver}.%{_target_cpu} \
    KBUILD_EXTRA_SYMBOLS=%{scst_module_symvers}


%install
make install DESTDIR=%{buildroot} SCST_INC_DIR=%{_includedir}/scst \
    SBINDIR=%{_sbindir} MANDIR=%{_mandir} KVER=%{kver}.%{_target_cpu} \
    KDIR=%{_usrsrc}/kernels/%{kver}.%{_target_cpu}
# move kmodules into the scst directory
mv %{buildroot}%{kmod_install_dir}/extra %{buildroot}%{kmod_install_dir}/scst

# init script
mkdir -p %{buildroot}%{_initrddir}
install -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}


%clean
rm -rf %{buildroot}


%files target-utils
%{_sbindir}/iscsi-scst-adm
%{_sbindir}/iscsi-scstd
%{_initrddir}/%{name}
%doc AskingQuestions COPYING ChangeLog README ToDo
%doc doc/iscsi-scst-howto.txt
%doc %{_mandir}


%files -n kmod-%{name}-%{kver}
%{kmod_install_dir}/scst/*.ko


%post -n kmod-%{name}-%{kver}
/sbin/depmod -aeF /boot/System.map-%{kver}.%{_target_cpu} \
    %{kver}.%{_target_cpu} > /dev/null || :


%postun -n kmod-%{name}-%{kver}
/sbin/depmod -aeF /boot/System.map-%{kver}.%{_target_cpu} \
    %{kver}.%{_target_cpu} > /dev/null || :


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
* Tue Jul 29 2014 John Morris <john@zultron.com> - 2.2.1-0
- Update to v. 2.2.1
- Update init script, cribbing from nslcd
- Fix macros
- Specfile modernizations
- Update BRs: and R:s
- Remove cruft
- Rename kernel-module-* pkgs to kmod-*
- Fix kbuild symbols
- Fix %%docs

* Mon Nov 23 2009  Jaroslaw Polok <jaroslaw.polok@cern.ch> 1.0.11-4.cern
- renamed iscsi-scst-utils package to iscsi-scst-target-utils for more
  consistency with other iscsi packages (scsi-target-utils)

* Fri Nov 20 2009  Andras HORVATH <andras.horvath@cern.ch> 1.0.11-3.cern
- added manpages and howto

* Mon Nov 16 2009  Jaroslaw Polok <jaroslaw.polok@cern.ch> 1.0.11-2.cern
- 2nd attempt at packaging ;-)

* Fri Nov 13 2009  Andras HORVATH <andras.horvath@cern.ch> 1.0.11-1.cern
- first packaging attempt
