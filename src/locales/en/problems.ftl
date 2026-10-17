# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## Package problems (packages spec). Every one has $file and $path: the
## file inside the package, and where in it.

problem-unreadable = { $file } can't be read: { $reason }
problem-missing-file = { $file } is missing.
problem-unknown-folder = { $file } is not a content folder.
problem-unexpected-file = { $file } doesn't belong there.
problem-syntax = { $file } is not valid JSON (line { $line }, column { $column }).
problem-not-an-entity = { $file } must hold an object or a list of objects.
problem-not-utf8 = { $file } isn't UTF-8 text.
problem-empty = { $file }, { $path }: the list can't be empty.
problem-unknown-field = { $file }, { $path }: unknown field "{ $field }".
problem-duplicate-field = { $file }, { $path }: the field "{ $field }" appears twice.
problem-missing-field = { $file }, { $path }: the field "{ $field }" is missing.
# $detail is the JSON parser's own description, in English.
problem-invalid-value = { $file }, { $path }: invalid value ({ $detail }).
problem-invalid-format = { $file }, { $path }: the value has the wrong format.
problem-out-of-range = { $file }, { $path }: the value is out of range.
problem-invalid-id = { $file }, { $path }: "{ $id }" is not a valid id.
problem-wrong-kind = { $file }, { $path }: "{ $id }" doesn't belong in this folder; ids here start with "{ $expected }:".
problem-duplicate-id = { $file }, { $path }: "{ $id }" is also defined in { $other }.
problem-unresolved-reference = { $file }, { $path }: nothing defines "{ $id }".
problem-wrong-count = The package must define exactly one entry in { $folder }, not { $count }.
problem-unsupported-genre = { $file }: the genre "{ $genre }" isn't supported.
problem-unknown-locale = { $file }: the locale "{ $locale }" isn't declared in the manifest.
problem-text-syntax = { $file }, line { $line }: the text isn't valid Fluent.
problem-missing-text = { $file }, { $path }: the message "{ $message }" is missing in { $locale }.
problem-invalid-mix = { $file }: region { $region } has no nationality to draw.
problem-empty-given-names = { $file }: { $nationality } has no given names.
problem-empty-family-names = { $file }: { $nationality } has no family names.
problem-no-roles = { $file }: the role set has no roles.
problem-duplicate-role = { $file }: the role { $role } appears twice.
problem-missing-weight = { $file }: the role { $role } has no weight for { $attribute }.
problem-zero-weights = { $file }: the weights of { $role } add up to zero.
problem-too-many-subs = { $file }: { $subs } subs, but only { $roles } roles.
problem-duplicate-nickname = { $file }, { $path }: { $player } and { $other } are both pinned with the nickname "{ $nickname }".
problem-nickname-pool = { $file }: { $distinct } distinct nicknames, but { $needed } are needed.
problem-incompletable-roster = { $file }: the pinned players of { $team } leave no room for { $roles }.
