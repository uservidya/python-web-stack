> Warning: Currently my priority is to hack together a workable prototype, so this document may be inaccurate. Please don't rely on anything written here, including command usages and config structures, including others, without consulting the source code.

# Python Web Stack

A complete web stack for Python WSGI applications. Called PWS onward.

## Scope

We'll build it with APT first. The stack consists of three parts: web server, WSGI server, and maintainance scripts. let's not contain any web frameworks by default (peace out, guys!), and just offer maintainace scripts to set up frameworks everyone wants, and just set up the path to the WSGI scripts.

### Web Server

Two choices here: Use the nginx provided by APT, or roll our own fork. I currently use the APT-based implementation, but think this may not be very suitable for other platforms. It's pretty difficult to maintain cross-platform compatibility when you need to configure system-based things. Maybe we'll need a seperate module for these platform-specific things (like what we're doing with formulae configurations).

#### APT-Based

##### Advantages

* Can easily integrate to the existed ecosystem
* Elegant (if designed correctly)
* Don't need extra mantainace

##### Disadvantages

* Depends on upstream support (possible slow update, backward incompatibility, etc.)
* Configuration can be a mess. Need to take account of possibility if user:
    1. Installs nginx
    2. Modifies nginx config
    3. Installs PWS
    4. Do something
    5. Removes PWS

    Now what do we do at 3. and 5.? If the user makes some incompatible configs in 2., we'll need to find them during 3., and maybe *save them* for reversion at 5.. APT's nginx uses `sites-available` and `sites-enabld` by default, so this may not be *that* much a problem, but still...

#### Roll Our Own

##### Advantages

* We can control the configs completely.
* Always have the latest version (as long as we maintain it). Even patch something if we need to.

##### Disadvantages

* Some people might not like it.
* Extra development overhead?

### WSGI Server

virtualenv + Gunicorn (inside env). Don't use supervisor for now because I want to have as much flexibility to a Windows port as possible.

#### No virtualenvwrapper?

Well you can always install it if you want to, don't you! This makes the setup minimal, and let us be able to configure things more freely. virtualenvwrapper requires some system integration (such as the `WORKON_HOME` environment variable) and is too fragile to user tweaks IMO.

#### virtualenv

I think the "ideal" way is to depend on `python-virtualenv`, but what will happen if the user installs (or wants to install) virtualenv without using APT? Need to check.

### Maintainance Scripts

Two scripts (probably need better names):

* `mksite`
* `rmsite`

#### `mksite`

`mksite django proj` create a new Django site named `proj`. Can have `mksite flask proj`, `mksite pyramid proj`, etc..

* Prompt for needed info.
* Prompt for the location to store the project. (Needs a sensible default.)

    This one is not currently implemented yet -- things are currently stored in the `envs` sub-directory. Will change, but where should this location be?

* Create the project.
* Create appropriate WSGI script if needed.

    Not currently implemented, since Django does not need it. Will corretly (if needed) when we add more formulae.

* Create a Gunicorn config file. (Where should this go? A central storage like Nginx config, or inside each project?)

    Not currently implemented. Need to write a startup script, but where best to put it? `/etc/init.d` is fine if we use APT.

* Create an appropriate Nginx config file in `sites-available` and link it to `sites-enabled`.
* Tweak some of the project's configuration. Django's `STATIC_ROOT` and `MEDIA_ROOT`, for example.

#### `rmsite`

`rmsite <sitename>` removes a site with name `<sitename>`

* Remove things created by `mksite django`. (Do we need to prompt for the project source files? Don't think so because the user might as well expect that. But still...)
* Prompt whether we should remove the tables, the database, and the owner (in that order).

    ...Or maybe just prompt for "database removal" and leave everything else to the user?



## Notes

### Dependencies

#### APT

* nginx

#### PIP

* gunicorn
