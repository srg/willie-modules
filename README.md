# willie-modules

*- a repository of modules for [willie](http://willie.dftba.net/)* 

###installation
the repository follows willie's local configuration folder's ~/.willie/ structure,
where modules from this repository (located in modules/), would be placed in ~/.willie/modules/.
in addition, we also have a conf-module/ folder containing configurations for some modules.

one could also use git to clone this repo into one's own ~/.willie/ folder (this is not recommended as many of our modules are likely to be broken):

- `cd ~/.willie/`
- `git clone https://github.com/teamsrg/willie-modules.git .`
- shitpost

the webload module can also be used to install modules from our repo. when installed and loaded,
use `webload list` for currently available modules, `webload sync module` to install desired module, and `webload update` to update all installed modules.

**please note that almost everything here is written and maintained by plebs**
