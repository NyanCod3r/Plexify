# Changelog

## [1.1.0](https://github.com/NyanCod3r/Plexify/compare/v1.3.2...v1.1.0) (2026-01-25)


### ⚠ BREAKING CHANGES

* SPOTIFY_REFRESH_TOKEN now required for 1-star deletion. Run generate_spotify_token.py once locally to obtain the token.

### Features

* Add OAuth refresh token support for Spotify playlist modifications ([e330b0d](https://github.com/NyanCod3r/Plexify/commit/e330b0dce318ca3306e5329f079f2a511baa01c6))
* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))
* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))
* **refactor:** BREAKING CHANGE: Plexify 2.0 ([e209951](https://github.com/NyanCod3r/Plexify/commit/e2099513352d13c4db03a1ad3ae670356f9144db))
* **sync:** Add support for playlist URIs and clarify add-only sync logic ([eaf4436](https://github.com/NyanCod3r/Plexify/commit/eaf44367a46653b475f45114bcc9ab7088985ff9))
* **sync:** Add support for playlist URIs and clarify add-only sync logic ([dcdd564](https://github.com/NyanCod3r/Plexify/commit/dcdd564db04474c2e0496de11cb9a3d17a3abc2b))
* **sync:** Add support for playlist URIs and clarify add-only sync logic ([3485f26](https://github.com/NyanCod3r/Plexify/commit/3485f26501db1ccc68d2b9118dd67e80faff3d0d))
* **sync:** Change logic to not remove tracks from Plex ([40a5bb6](https://github.com/NyanCod3r/Plexify/commit/40a5bb6973ea47bde8723bfc4f9d39485f62e774))


### Bug Fixes

* **ci:** Add pre-release test job and fix failing test ([bac845f](https://github.com/NyanCod3r/Plexify/commit/bac845fe3b0d1c1688caa2ae454364cbdf810472))
* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))
* **ci:** Correct Dockerfile paths and test environment[BREACKING CHANGE] ([8d98105](https://github.com/NyanCod3r/Plexify/commit/8d98105bee5eb3b2d7ed586612881aaca500f12e))
* **ci:** Fix docker build context and test paths ([d11967f](https://github.com/NyanCod3r/Plexify/commit/d11967f1aeece4a24df4aee4b9bda18f4ec52a49))
* **ci:** Set PYTHONPATH for tests in Docker ([c33d5bd](https://github.com/NyanCod3r/Plexify/commit/c33d5bd8558122a9d9f152ccac8ce50351579ee7))
* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))
* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))
* **ci:** Standardize spotify environment variables to SPOTIPY ([1b3c4d1](https://github.com/NyanCod3r/Plexify/commit/1b3c4d14a86b1ba92d3d78bd91bb9956eedcda5c))
* **ci:** Standardize spotify environment variables to SPOTIPY ([b0df9ff](https://github.com/NyanCod3r/Plexify/commit/b0df9ff26d3948a9b7444a6dad8d1af1c370b7dd))
* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **docs:** Add demo video to README.md ([0b7a932](https://github.com/NyanCod3r/Plexify/commit/0b7a932afdb168187621f75ce630052c80d7d415))
* **docs:** Add README guidelines to local prompt instructions ([62ae104](https://github.com/NyanCod3r/Plexify/commit/62ae1044fc0f0b6ec1892d84a49cc6a2fb580fac))
* **plex_utils:** Fixed download issue due to incorrect coding ([28b946e](https://github.com/NyanCod3r/Plexify/commit/28b946eaaa16645d85bc6c07d7b5bc7f372b3530))
* **plex_utils:** Removed API Throttle ([5cb065c](https://github.com/NyanCod3r/Plexify/commit/5cb065ca0d8abe664f88b707048e6d5bb19a3115))
* **plex_utils:** Test dropping Plex Playlists ([ebf72a8](https://github.com/NyanCod3r/Plexify/commit/ebf72a8a36561766d3ad079c452a0114363f157e))
* **plex:** Add missing getPlexPlaylists function ([be8c245](https://github.com/NyanCod3r/Plexify/commit/be8c245025559cf16049b353300b60500913c27a))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))
* **sync:** Apply local fixes to sync and utils ([8c3458d](https://github.com/NyanCod3r/Plexify/commit/8c3458dceda8a56013badd922de4e035c618405a))
* **sync:** Make Discover Weekly/Release Radar 1:1 and delete local files when removing tracks from Plex playlists ([6917c13](https://github.com/NyanCod3r/Plexify/commit/6917c134780458d90fcf921c458cc5b3e9fb59a8))
* test Test ([24afc5d](https://github.com/NyanCod3r/Plexify/commit/24afc5d5603a81d93ecda5647c588550cf2d4ed1))
* **tests:** Correct mock data and patch targets in unit tests ([57fb9de](https://github.com/NyanCod3r/Plexify/commit/57fb9de4f758a8a77e80c50264c8bc32fc35d7ef))
* **tests:** Correct mock for plex.search in test_getPlexTracks ([03970ae](https://github.com/NyanCod3r/Plexify/commit/03970ae7c05937d1a077ded4f28e413e40cb51cb))
* **tests:** Fix test_runSync argument count and show full code ([c0bb55b](https://github.com/NyanCod3r/Plexify/commit/c0bb55bef1042a56c98bc9b3d906c5b96b74af82))
* **tests:** Refactor test_main.py to align with current app structure ([bb34054](https://github.com/NyanCod3r/Plexify/commit/bb34054b1bdedb3d710b0d34fd4317f13031f3b9))
* **tests:** Remove import of missing delete_unmatched_files from test_main.py ([7b57ee2](https://github.com/NyanCod3r/Plexify/commit/7b57ee2d92cb3cb03cb1a1cda9a46b4ddf07cb28))


### Documentation

* README Test of beta, Dropped Plex playlists ([b58b92d](https://github.com/NyanCod3r/Plexify/commit/b58b92d94e066315df5a5dab5cbbcb8206af1a21))


### Miscellaneous Chores

* **master:** release 1.1.0 ([3ca3619](https://github.com/NyanCod3r/Plexify/commit/3ca3619dc35960c3d462bd26e1a55c581014b6d2))
* **master:** release 1.2.0-beta ([#6](https://github.com/NyanCod3r/Plexify/issues/6)) ([d5dedae](https://github.com/NyanCod3r/Plexify/commit/d5dedaec0df4d46e1ac641dc405a8725105a8505))

## [1.3.2](https://github.com/NyanCod3r/Plexify/compare/v1.3.1...v1.3.2) (2025-11-03)


### Bug Fixes

* **plex_utils:** Fixed download issue due to incorrect coding ([28b946e](https://github.com/NyanCod3r/Plexify/commit/28b946eaaa16645d85bc6c07d7b5bc7f372b3530))

## [1.3.1](https://github.com/NyanCod3r/Plexify/compare/v1.3.0...v1.3.1) (2025-11-01)


### Bug Fixes

* **docs:** Add README guidelines to local prompt instructions ([62ae104](https://github.com/NyanCod3r/Plexify/commit/62ae1044fc0f0b6ec1892d84a49cc6a2fb580fac))
* **plex_utils:** Removed API Throttle ([5cb065c](https://github.com/NyanCod3r/Plexify/commit/5cb065ca0d8abe664f88b707048e6d5bb19a3115))
* **sync:** Make Discover Weekly/Release Radar 1:1 and delete local files when removing tracks from Plex playlists ([6917c13](https://github.com/NyanCod3r/Plexify/commit/6917c134780458d90fcf921c458cc5b3e9fb59a8))

## [1.3.0](https://github.com/NyanCod3r/Plexify/compare/v1.2.0...v1.3.0) (2025-10-30)


### Features

* **sync:** Add support for playlist URIs and clarify add-only sync logic ([eaf4436](https://github.com/NyanCod3r/Plexify/commit/eaf44367a46653b475f45114bcc9ab7088985ff9))
* **sync:** Add support for playlist URIs and clarify add-only sync logic ([dcdd564](https://github.com/NyanCod3r/Plexify/commit/dcdd564db04474c2e0496de11cb9a3d17a3abc2b))
* **sync:** Add support for playlist URIs and clarify add-only sync logic ([3485f26](https://github.com/NyanCod3r/Plexify/commit/3485f26501db1ccc68d2b9118dd67e80faff3d0d))


### Bug Fixes

* **sync:** Apply local fixes to sync and utils ([8c3458d](https://github.com/NyanCod3r/Plexify/commit/8c3458dceda8a56013badd922de4e035c618405a))
* **tests:** Fix test_runSync argument count and show full code ([c0bb55b](https://github.com/NyanCod3r/Plexify/commit/c0bb55bef1042a56c98bc9b3d906c5b96b74af82))
* **tests:** Remove import of missing delete_unmatched_files from test_main.py ([7b57ee2](https://github.com/NyanCod3r/Plexify/commit/7b57ee2d92cb3cb03cb1a1cda9a46b4ddf07cb28))

## [1.2.0](https://github.com/NyanCod3r/Plexify/compare/v1.1.0...v1.2.0) (2025-10-26)


### Features

* **sync:** Change logic to not remove tracks from Plex ([40a5bb6](https://github.com/NyanCod3r/Plexify/commit/40a5bb6973ea47bde8723bfc4f9d39485f62e774))


### Bug Fixes

* **plex:** Add missing getPlexPlaylists function ([be8c245](https://github.com/NyanCod3r/Plexify/commit/be8c245025559cf16049b353300b60500913c27a))

## [1.1.0](https://github.com/NyanCod3r/Plexify/compare/v1.1.0...v1.1.0) (2025-10-26)


### Features

* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))
* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))


### Bug Fixes

* **ci:** Add pre-release test job and fix failing test ([bac845f](https://github.com/NyanCod3r/Plexify/commit/bac845fe3b0d1c1688caa2ae454364cbdf810472))
* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))
* **ci:** Correct Dockerfile paths and test environment[BREACKING CHANGE] ([8d98105](https://github.com/NyanCod3r/Plexify/commit/8d98105bee5eb3b2d7ed586612881aaca500f12e))
* **ci:** Fix docker build context and test paths ([d11967f](https://github.com/NyanCod3r/Plexify/commit/d11967f1aeece4a24df4aee4b9bda18f4ec52a49))
* **ci:** Set PYTHONPATH for tests in Docker ([c33d5bd](https://github.com/NyanCod3r/Plexify/commit/c33d5bd8558122a9d9f152ccac8ce50351579ee7))
* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))
* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))
* **ci:** Standardize spotify environment variables to SPOTIPY ([1b3c4d1](https://github.com/NyanCod3r/Plexify/commit/1b3c4d14a86b1ba92d3d78bd91bb9956eedcda5c))
* **ci:** Standardize spotify environment variables to SPOTIPY ([b0df9ff](https://github.com/NyanCod3r/Plexify/commit/b0df9ff26d3948a9b7444a6dad8d1af1c370b7dd))
* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))
* **tests:** Correct mock data and patch targets in unit tests ([57fb9de](https://github.com/NyanCod3r/Plexify/commit/57fb9de4f758a8a77e80c50264c8bc32fc35d7ef))
* **tests:** Correct mock for plex.search in test_getPlexTracks ([03970ae](https://github.com/NyanCod3r/Plexify/commit/03970ae7c05937d1a077ded4f28e413e40cb51cb))
* **tests:** Refactor test_main.py to align with current app structure ([bb34054](https://github.com/NyanCod3r/Plexify/commit/bb34054b1bdedb3d710b0d34fd4317f13031f3b9))


### Miscellaneous Chores

* **master:** release 1.1.0 ([3ca3619](https://github.com/NyanCod3r/Plexify/commit/3ca3619dc35960c3d462bd26e1a55c581014b6d2))
* **master:** release 1.2.0-beta ([#6](https://github.com/NyanCod3r/Plexify/issues/6)) ([d5dedae](https://github.com/NyanCod3r/Plexify/commit/d5dedaec0df4d46e1ac641dc405a8725105a8505))

## [1.1.0](https://github.com/NyanCod3r/Plexify/compare/v1.1.0...v1.1.0) (2025-10-26)


### Features

* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))
* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))


### Bug Fixes

* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))
* **ci:** Correct Dockerfile paths and test environment[BREACKING CHANGE] ([8d98105](https://github.com/NyanCod3r/Plexify/commit/8d98105bee5eb3b2d7ed586612881aaca500f12e))
* **ci:** Fix docker build context and test paths ([d11967f](https://github.com/NyanCod3r/Plexify/commit/d11967f1aeece4a24df4aee4b9bda18f4ec52a49))
* **ci:** Set PYTHONPATH for tests in Docker ([c33d5bd](https://github.com/NyanCod3r/Plexify/commit/c33d5bd8558122a9d9f152ccac8ce50351579ee7))
* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))
* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))
* **ci:** Standardize spotify environment variables to SPOTIPY ([1b3c4d1](https://github.com/NyanCod3r/Plexify/commit/1b3c4d14a86b1ba92d3d78bd91bb9956eedcda5c))
* **ci:** Standardize spotify environment variables to SPOTIPY ([b0df9ff](https://github.com/NyanCod3r/Plexify/commit/b0df9ff26d3948a9b7444a6dad8d1af1c370b7dd))
* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))
* **tests:** Correct mock data and patch targets in unit tests ([57fb9de](https://github.com/NyanCod3r/Plexify/commit/57fb9de4f758a8a77e80c50264c8bc32fc35d7ef))
* **tests:** Refactor test_main.py to align with current app structure ([bb34054](https://github.com/NyanCod3r/Plexify/commit/bb34054b1bdedb3d710b0d34fd4317f13031f3b9))


### Miscellaneous Chores

* **master:** release 1.1.0 ([3ca3619](https://github.com/NyanCod3r/Plexify/commit/3ca3619dc35960c3d462bd26e1a55c581014b6d2))
* **master:** release 1.2.0-beta ([#6](https://github.com/NyanCod3r/Plexify/issues/6)) ([d5dedae](https://github.com/NyanCod3r/Plexify/commit/d5dedaec0df4d46e1ac641dc405a8725105a8505))

## [1.1.0](https://github.com/NyanCod3r/Plexify/compare/v1.1.1...v1.1.0) (2025-10-26)


### Features

* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))
* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))


### Bug Fixes

* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))
* **ci:** Correct Dockerfile paths and test environment[BREACKING CHANGE] ([8d98105](https://github.com/NyanCod3r/Plexify/commit/8d98105bee5eb3b2d7ed586612881aaca500f12e))
* **ci:** Fix docker build context and test paths ([d11967f](https://github.com/NyanCod3r/Plexify/commit/d11967f1aeece4a24df4aee4b9bda18f4ec52a49))
* **ci:** Set PYTHONPATH for tests in Docker ([c33d5bd](https://github.com/NyanCod3r/Plexify/commit/c33d5bd8558122a9d9f152ccac8ce50351579ee7))
* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))
* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))
* **ci:** Standardize spotify environment variables to SPOTIPY ([1b3c4d1](https://github.com/NyanCod3r/Plexify/commit/1b3c4d14a86b1ba92d3d78bd91bb9956eedcda5c))
* **ci:** Standardize spotify environment variables to SPOTIPY ([b0df9ff](https://github.com/NyanCod3r/Plexify/commit/b0df9ff26d3948a9b7444a6dad8d1af1c370b7dd))
* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))
* **tests:** Refactor test_main.py to align with current app structure ([bb34054](https://github.com/NyanCod3r/Plexify/commit/bb34054b1bdedb3d710b0d34fd4317f13031f3b9))


### Miscellaneous Chores

* **master:** release 1.1.0 ([3ca3619](https://github.com/NyanCod3r/Plexify/commit/3ca3619dc35960c3d462bd26e1a55c581014b6d2))
* **master:** release 1.2.0-beta ([#6](https://github.com/NyanCod3r/Plexify/issues/6)) ([d5dedae](https://github.com/NyanCod3r/Plexify/commit/d5dedaec0df4d46e1ac641dc405a8725105a8505))

## [1.1.1](https://github.com/NyanCod3r/Plexify/compare/v1.1.0...v1.1.1) (2025-10-26)


### Bug Fixes

* **ci:** Fix docker build context and test paths ([d11967f](https://github.com/NyanCod3r/Plexify/commit/d11967f1aeece4a24df4aee4b9bda18f4ec52a49))

## [1.1.0](https://github.com/NyanCod3r/Plexify/compare/v1.1.0...v1.1.0) (2025-10-26)


### Features

* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))
* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))


### Bug Fixes

* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))
* **ci:** Correct Dockerfile paths and test environment[BREACKING CHANGE] ([8d98105](https://github.com/NyanCod3r/Plexify/commit/8d98105bee5eb3b2d7ed586612881aaca500f12e))
* **ci:** Set PYTHONPATH for tests in Docker ([c33d5bd](https://github.com/NyanCod3r/Plexify/commit/c33d5bd8558122a9d9f152ccac8ce50351579ee7))
* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))
* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))
* **ci:** Standardize spotify environment variables to SPOTIPY ([1b3c4d1](https://github.com/NyanCod3r/Plexify/commit/1b3c4d14a86b1ba92d3d78bd91bb9956eedcda5c))
* **ci:** Standardize spotify environment variables to SPOTIPY ([b0df9ff](https://github.com/NyanCod3r/Plexify/commit/b0df9ff26d3948a9b7444a6dad8d1af1c370b7dd))
* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))


### Miscellaneous Chores

* **master:** release 1.1.0 ([3ca3619](https://github.com/NyanCod3r/Plexify/commit/3ca3619dc35960c3d462bd26e1a55c581014b6d2))
* **master:** release 1.2.0-beta ([#6](https://github.com/NyanCod3r/Plexify/issues/6)) ([d5dedae](https://github.com/NyanCod3r/Plexify/commit/d5dedaec0df4d46e1ac641dc405a8725105a8505))

## [1.1.0](https://github.com/NyanCod3r/Plexify/compare/v1.3.2-beta...v1.1.0) (2025-10-26)


### Features

* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))
* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))


### Bug Fixes

* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))
* **ci:** Set PYTHONPATH for tests in Docker ([c33d5bd](https://github.com/NyanCod3r/Plexify/commit/c33d5bd8558122a9d9f152ccac8ce50351579ee7))
* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))
* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))
* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))


### Miscellaneous Chores

* **master:** release 1.1.0 ([3ca3619](https://github.com/NyanCod3r/Plexify/commit/3ca3619dc35960c3d462bd26e1a55c581014b6d2))
* **master:** release 1.2.0-beta ([#6](https://github.com/NyanCod3r/Plexify/issues/6)) ([d5dedae](https://github.com/NyanCod3r/Plexify/commit/d5dedaec0df4d46e1ac641dc405a8725105a8505))

## [1.3.2-beta](https://github.com/NyanCod3r/Plexify/compare/v1.3.1-beta...v1.3.2-beta) (2025-10-26)


### Bug Fixes

* **ci:** Specify correct Dockerfile path in build workflow ([520d177](https://github.com/NyanCod3r/Plexify/commit/520d1771a77944ad33fa7311758e52f02cb4a515))

## [1.3.1-beta](https://github.com/NyanCod3r/Plexify/compare/v1.3.0-beta...v1.3.1-beta) (2025-10-26)


### Bug Fixes

* **ci:** Adjust docker build context to include tests ([25d30f8](https://github.com/NyanCod3r/Plexify/commit/25d30f8db7ed844e83fe58f975b2cdb1d6d610b2))

## [1.3.0-beta](https://github.com/NyanCod3r/Plexify/compare/v1.2.0-beta...v1.3.0-beta) (2025-10-26)


### Features

* **ci:** Add manual workflow dispatch for stable releases ([7fb2a05](https://github.com/NyanCod3r/Plexify/commit/7fb2a05070d1467097402749d75d6639963a3611))


### Bug Fixes

* **ci:** Simplify release workflow to be commit-driven ([5b54260](https://github.com/NyanCod3r/Plexify/commit/5b542602508577509310fa86b1f832ddf4467c7e))

## [1.2.0-beta](https://github.com/NyanCod3r/Plexify/compare/v1.1.1-beta...v1.2.0-beta) (2025-10-26)


### Features

* **ci:** Automate semantic versioning with release-please[BREACKING CHANGE] ([19f404b](https://github.com/NyanCod3r/Plexify/commit/19f404b360eda179199c632652a5dccbb4bba68a))


### Bug Fixes

* **ci:** Trigger docker build on release creation[BREAKING CHANGE] ([b087719](https://github.com/NyanCod3r/Plexify/commit/b0877191da250056a4375f3015f06999aaa6073d))
* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
* **ci:** updated deprecated commands ([8dad227](https://github.com/NyanCod3r/Plexify/commit/8dad227d5ec420e336fa3d187c1fc3adf69f0850))
* **plex:** Improve download handling and path sanitization ([b16bb33](https://github.com/NyanCod3r/Plexify/commit/b16bb33a86b2e37f63669c9fb8e457f07fdf5167))

## [1.1.1-beta](https://github.com/NyanCod3r/Plexify/compare/v1.1.0-beta...v1.1.1-beta) (2025-10-26)


### Bug Fixes

* **ci:** Trigger docker build on release creation[PATCH] ([41038fc](https://github.com/NyanCod3r/Plexify/commit/41038fc45158aa234e3297b83c2ba15001c939ee))
* **ci:** Trigger docker build on release creation[PATCH] ([23bb4a7](https://github.com/NyanCod3r/Plexify/commit/23bb4a7948f447efdaed78ba0da3ae82c4340b8f))
