%bcond_without tests
%bcond_without weak_deps

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __provides_exclude_from ^/opt/ros/iron/.*$
%global __requires_exclude_from ^/opt/ros/iron/.*$

Name:           ros-iron-flexbe-onboard
Version:        3.0.0
Release:        1%{?dist}%{?release_suffix}
Summary:        ROS flexbe_onboard package

License:        BSD
URL:            http://ros.org/wiki/flexbe_core
Source0:        %{name}-%{version}.tar.gz

Requires:       ros-iron-flexbe-core
Requires:       ros-iron-flexbe-msgs
Requires:       ros-iron-flexbe-states
Requires:       ros-iron-launch-ros
Requires:       ros-iron-rclpy
Requires:       ros-iron-ros-workspace
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  ros-iron-flexbe-core
BuildRequires:  ros-iron-flexbe-msgs
BuildRequires:  ros-iron-flexbe-states
BuildRequires:  ros-iron-launch-ros
BuildRequires:  ros-iron-rclpy
BuildRequires:  ros-iron-ros-workspace
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}
Provides:       %{name}-runtime = %{version}-%{release}

%if 0%{?with_tests}
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  ros-iron-ament-copyright
BuildRequires:  ros-iron-ament-flake8
BuildRequires:  ros-iron-ament-pep257
BuildRequires:  ros-iron-launch-testing
%endif

%description
flexbe_onboard implements the robot-side of the behavior engine from where all
behaviors are started.

%prep
%autosetup -p1

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/iron/setup.sh" ]; then . "/opt/ros/iron/setup.sh"; fi
%py3_build

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/iron/setup.sh" ]; then . "/opt/ros/iron/setup.sh"; fi
%py3_install -- --prefix "/opt/ros/iron"

%if 0%{?with_tests}
%check
# Look for a directory with a name indicating that it contains tests
TEST_TARGET=$(ls -d * | grep -m1 "\(test\|tests\)" ||:)
if [ -n "$TEST_TARGET" ] && %__python3 -m pytest --version; then
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/iron/setup.sh" ]; then . "/opt/ros/iron/setup.sh"; fi
%__python3 -m pytest $TEST_TARGET || echo "RPM TESTS FAILED"
else echo "RPM TESTS SKIPPED"; fi
%endif

%files
/opt/ros/iron

%changelog
* Wed May 01 2024 Philipp Schillinger <philsplus@gmail.com> - 3.0.0-1
- Autogenerated by Bloom

* Thu Aug 10 2023 Philipp Schillinger <philsplus@gmail.com> - 2.3.3-1
- Autogenerated by Bloom

