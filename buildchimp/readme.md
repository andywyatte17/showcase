## buildchimp

This is a program built using PySide (Python + Qt) that

---

## TODO

* Recent File List
  * Remove item when an attempt to open a recent file fails.
  * Limit most recent item list to, say, 10 items.
  * Add Clear Recent Items menu in File > Open Recent.
* user.yaml config files
  * For the file BuildIt.yaml the user can put a file BuildIt.user.yaml in the same folder.
  * When processing BuildIt.yaml in buildchimp, BuildIt.user.yaml is loaded second and any settings within BuildIt.user.yaml *replace* the equivalent BuildIt.yaml settings.
  * Uses:
    * Replace settings in the globals > environment area.
    * Another use might be to add additional *buildsteps* for special purposes. 
