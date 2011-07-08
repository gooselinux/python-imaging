%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%define pyver %(%{__python} -c "import sys ; print sys.version[:3]")
%define py_incdir %{_includedir}/python%{pyver}

Summary:       Python's own image processing library
Name:          python-imaging
Version:       1.1.6
Release:       19%{?dist}

License:       MIT
Group:         System Environment/Libraries

Source0:       http://effbot.org/downloads/Imaging-%{version}.tar.gz
Patch0:        %{name}-no-xv.patch
Patch1:        %{name}-lib64.patch
Patch2:        %{name}-giftrans.patch
Patch3:        %{name}-1.1.6-sane-types.patch
Patch4:        %{name}-shebang.patch
URL:           http://www.pythonware.com/products/pil/
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: python-devel, libjpeg-devel, zlib-devel, freetype-devel
BuildRequires: tkinter, tk-devel
%ifnarch s390 s390x
BuildRequires: sane-backends-devel
%endif

%description
Python Imaging Library

The Python Imaging Library (PIL) adds image processing capabilities
to your Python interpreter.

This library provides extensive file format support, an efficient
internal representation, and powerful image processing capabilities.

Notice that in order to reduce the package dependencies there are
three subpackages: devel (for development); tk (to interact with the
tk interface) and sane (scanning devices interface).

%package devel
Summary: Development files for python-imaging
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}, python-devel
Requires: libjpeg-devel
Requires: zlib-devel

%description devel
Development files for python-imaging.

%ifnarch s390 s390x
%package sane
Summary: Python Module for using scanners
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description sane
This package contains the sane module for Python which provides access to
various raster scanning devices such as flatbed scanners and digital cameras.
%endif

%package tk
Summary: Tk interface for python-imaging
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}
Requires: tkinter
Obsoletes: %{name} < 1.1.6-3
Conflicts: %{name} < 1.1.6-3

%description tk
This package contains a Tk interface for python-imaging.

%prep
%setup -q -n Imaging-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1 -b .sane-types
%patch4 -p1 -b .shebang

# fix the interpreter path for Scripts/*.py
cd Scripts
for scr in *.py
do
  sed -e "s|/usr/local/bin/python|%{_bindir}/python|"  $scr > tmp.py
  mv tmp.py $scr
  chmod 755 $scr
done

%build
# Is this still relevant? (It was used in 1.1.4)
#%ifarch x86_64
#   CFLAGS="$RPM_OPT_FLAGS -fPIC -DPIC" \
#%endif

CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing" %{__python} setup.py build

%ifnarch s390 s390x
pushd Sane
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{py_incdir}/Imaging
install -m 644 libImaging/*.h $RPM_BUILD_ROOT/%{py_incdir}/Imaging
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%ifnarch s390 s390x
pushd Sane
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd
%endif

# There is no need to ship the binaries since they are already packaged
# in %doc
rm -rf $RPM_BUILD_ROOT%{_bindir}

# Separate files that need Tk and files that don't
echo '%%defattr (0644,root,root,755)' > files.main
echo '%%defattr (0644,root,root,755)' > files.tk
p="$PWD"

pushd $RPM_BUILD_ROOT%{python_sitearch}/PIL
for file in *; do
    case "$file" in
    ImageTk*|SpiderImagePlugin*|_imagingtk.so)
        what=files.tk
        ;;
    *)
        what=files.main
        ;;
    esac
    echo %{python_sitearch}/PIL/$file >> "$p/$what"
done
popd


%check
PYTHONPATH=$(ls -1d build/lib.linux*) %{__python} selftest.py

%clean
rm -rf $RPM_BUILD_ROOT


%files -f files.main
%defattr (-,root,root,-)
%doc README CHANGES
%{python_sitearch}/PIL.pth
%dir %{python_sitearch}/PIL

%files devel
%defattr (0644,root,root,755)
%{py_incdir}/Imaging
%doc Docs Scripts Images

%ifnarch s390 s390x
%files sane
%defattr (0644,root,root,755)
%doc Sane/CHANGES Sane/demo*.py Sane/sanedoc.txt
%if 0%{?fedora} >= 9 || 0%{?rhel} >= 6
%{python_sitearch}/pysane*egg-info
%endif
%{python_sitearch}/_sane.so
%{python_sitearch}/sane.py*
%endif

%files tk -f files.tk

%changelog
* Mon Jun 14 2010 Roman Rakus <rrakus@redhat.com> - 1.1.6-19
- Use -fno-strict-aliasing CFLAG
  Resolves: #596200

* Wed Feb 24 2010 Roman Rakus <rrakus@redhat.com> - 1.1.6-18
- Changed License to the MIT (Historical Permission Notice and Disclaimer)

* Fri Nov 13 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.1.6-17.1
- Fix conditional for RHEL

* Tue Sep 08 2009 Joel Granados <jgranado@redhat.com> - 1.1.6-17
- Fix the shebang issue.  See https://fedoraproject.org/wiki/Features/SystemPythonExecutablesUseSystemPython

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Apr 15 2009 Karsten Hopp <karsten@redhat.com> 1.1.6-15
- disable sane subpackage and sane requirements for mainframes, we don't have
  sane on s390 and s390x

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.1.6-13
- Rebuild for Python 2.6

* Thu Oct  2 2008 José Matos <jamatos[AT]fc.up.pt> - 1.1.6-12
- all patches are applied with -p1

* Thu Oct  2 2008 José Matos <jamatos[AT]fc.up.pt> - 1.1.6-11
- rebuild to avoid the patches fuzziness (#464984)

* Tue Jun 3 2008 Joel Granados <jgranado@redhat.com> - 1.1.6-10
- Fix the build.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.1.6-9
- Autorebuild for GCC 4.3

* Fri Jan  4 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.6-8
- Egg for PIL library is already in subdirectory, and found by glob.

* Fri Jan  4 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.6-7
- python_sitelib -> python_sitearch

* Fri Jan  4 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.6-6
- Support for Python Eggs for F9+

* Thu Jan  3 2008 José Matos <jamatos[AT]fc.up.pt> - 1.1.6-5
- Rebuild for Tcl/Tk upgrade (F9+).
- Update description to reflect the subpackages.
- Fix files permission.

* Tue Aug 28 2007 José Matos <jamatos[AT]fc.up.pt> - 1.1.6-4
- Rebuild for devel (F8).

* Sun Apr 29 2007 Nils Philippsen <nphilipp@redhat.com> - 1.1.6-3
- add sane subpackage, split off tk subpackage (#238252)
- add sane-types patch
- use -b for patches to save original files
- correct groups

* Wed Feb 14 2007 José Matos <jamatos[AT]fc.up.pt> - 1.1.6-2
- Rebuild for Tcl/Tk downgrade (F7)

* Mon Feb  5 2007 José Matos <jamatos[AT]fc.up.pt> - 1.1.6-1
- New upstream version.
- Clean spec file and specify license as BSD.

* Tue Dec 12 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-7
- Rebuild for python 2.5.

* Tue Aug 29 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-6
- Rebuild for FE6
- Clean package, no need for python-abi requirement and ghost pyo files

* Thu Apr  6 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-5
- Rebuild because of #187739

* Tue Apr  4 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-4
- Rebuild

* Tue Apr  4 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-3
- Restore gif transparency patch. (bug #187875)

* Sun Apr  2 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-2
- Fix bug #185203 (Thanks to Rick L Vinyard Jr)

* Sun Mar  5 2006 José Matos <jamatos[AT]fc.up.pt> - 1.1.5-1
- Update to 1.1.5

* Sun May 22 2005 Jeremy Katz <katzj@redhat.com> - 1.1.4-9
- rebuild on all arches

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Mon Feb  7 2005 Thorsten Leemhuis <fedora at leemhuis dot info> - 0:1.1.4-7
- Build PIC on x86_64 to fix x86_64 linking.

* Sat Oct  9 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.1.4-6
- Borrow parts from patch in Debian's 1.1.4-3 to fix issues in bug 1038 as
  well as a bunch of others.
- Bring up to date with current fedora.us Python spec template recommendations.
- Fix -devel directory permissions.

* Sun Nov 30 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.4-0.fdr.5
- added -devel package (thanks to patch from pmatilai@welho.com)
- FC1 requires dependency to tcl-devel and tk-devel package

* Wed Jul 16 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.4-0.fdr.4
- bumped release
- implemented changes from Ville, which basically means that:
- setup macro now users "-q" option
- libpng dropped from buildrequirements
- run test suite after build

* Sat Jul 12 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.4-0.fdr.3
- fixed source0 to point into effbot.org instead of pythonware.com
- changed references from python2 to python, since python in RH9 is
  python 2.2.
- removed percent signs from changelog.

* Tue Jul 08 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.4-0.fdr.2
- added XFree86-devel and tkinter into buildrequires.
- removed version info from buildrequires
- removed unnecessary stuff from requires.

* Wed Jun 23 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.4-0.fdr.1
- new upstream version

* Tue May 20 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.3-0.fdr.5
- added python2-devel into buildrequires.
- added versionm variable into setup macro instead of hard coded
  version number.

* Mon May 12 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.3-0.fdr.4
- removed unnecessary ./configure
- /usr/lib -> _libdir macro
- smp flags to make

* Sat May 03 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.3-0.fdr.3
- changed buildroot macro back to $RP_BUILD_ROOT
- ./configure to configure macro
- Group to Development/Languages
- Added Epoch values to versioned Requires and BuildRequires
- added README and CHANGES-113 into doc

* Wed Mar 26 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.3-0.fdr.2
- added Epoch
- added URL into Source0
- replaced $RPM_BUILD_ROOT with buildroot macro

* Wed Mar 26 2003 Juha Ylitalo <jylitalo@iki.fi> - 0:1.1.3-0.fdr.1
- modified spec file to fit with fedora guidelines.

* Mon Sep 23 2002 Juha Ylitalo <jylitalo@iki.fi> - 1.1.3-1
- updated to 1.1.3
- switched from python 1.5.2 to python 2.2
- other modifications to make it build at minimal effort

* Tue Sep 12 2000 Ray Garcia <rayg@ssec.wisc.edu>
- update to 1.1

* Thu Mar 30 2000 Frederic Lepied <flepied@mandrakesoft.com> 1.0b1-3mdk
- group fix.

* Mon Jan 10 2000 Lenny Cartier <lenny@mandrakesoft.com>
- build for oxygen
- deactivate provinding of tkinter lib since Chmouel one's works perfectly

* Mon Dec 27 1999 Lenny Cartier <lenny@mandrakesoft.com>
- new in contribs
- bz2 archive

* Mon Jan 11 1999 Oliver Andrich <oli@andrich.net>
- upgraded to Imaging 1.0b1

* Sun Dec 27 1998 Oliver Andrich <oli@andrich.net>
- changed Setup file so that the tkinter module is compiled with Tix and BLT
  support

* Mon Jul 20 1998 Oliver Andrich <oli@andrich.net>
- had to recompile and update the package to support the uptodate graphics
  libs

* Sat Jun 07 1998 Oliver Andrich <oli@andrich.net>
- updated package to version 0.3a4

