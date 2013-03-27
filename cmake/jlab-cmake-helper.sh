#!/bin/bash

#   Copyright (C) 2013~2013 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

action=$1
shift

# TODO
CMAKE_EXECUTABLE=cmake

unique_name_from_file() {
    fname=$1
    target_prefix=$(echo -n "$fname" | tr '\n' ' ' | \
        sed -e 's/[^-._a-zA-Z0-9]/_/g')
    md5sum=$(${CMAKE_EXECUTABLE} -E md5sum <(echo -n "$fname"))
    md5sum=${md5sum%% *}
    echo -n "${target_prefix}-${md5sum}"
}

case "$action" in
    --unique-name)
        name=$1
        unique_name_from_file "$name"
        ;;
    --dummy)
        ;;
esac
