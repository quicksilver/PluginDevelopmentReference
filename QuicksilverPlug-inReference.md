# Quicksilver Plug-ins #

A haphazard reference by Rob McBroom <qsplugins@skurfer.com> with contributions from

  * Henning Jungkurth
  * Patrick Robertson
  * Etienne Samson
  * Ankur Kothari

<!--
TODO remove unneeded things from template
TODO QSBundleChildHandlers in the template is wrong
-->

## Intro ##

I wanted to write a plug-in. I found a bit of documentation on adding Actions, but that was about it. The rest was trial and error and stabbing in the dark (with some help from looking at existing plug-ins). I hope to spare others some of this frustration by documenting what I discovered. This is mainly a collection of random notes, rather than a step-by-step guide.

I'll assume you're working on a plug-in called "Blah" when giving examples.

## Getting Started ##

To compile most plug-ins, you'll need to build Quicksilver itself [from source][qssource]. (It'll put the stuff you need in `/tmp/QS`.) To build your plug-in with the Debug configuration, you'll need to first build Quicksilver with its Debug configuration. Same for the Release configuration.

To create a new plug-in:

  1. [Install Cookiecutter][icc]
  2. Run `cookiecutter https://github.com/quicksilver/plugin_template`
  3. Open the new project in Xcode

You should now have a plug-in that will build. If you want to use [Scripting Bridge](#scripting_bridge), see the additional steps in that section.

Now might be a good time to create your Git repository and make the initial commit.

Many of the items in the template's `Info.plist` are named "SomethingTemplate". This prevents Quicksilver from having to process unused features. If you need to use settings in any of these sections, just rename them, removing "Template" from the end.

[ghref]: https://github.com/quicksilver/PluginDevelopmentReference
[qssource]: https://github.com/quicksilver/Quicksilver
[icc]: https://cookiecutter.readthedocs.io/en/latest/installation.html

## Documentation and `bltrversion` ##

Before we get into the technical stuff, make sure you **provide adequate documentation** with any plug-in you create. This also goes for existing plug-ins that you're updating or fixing. Quicksilver plug-ins are notoriously light on documentation and as a result, people don't discover some of their best features for years. If you're not afraid to screw with the code, don't be afraid to screw with the documentation as well.

The best place to document your plug-in is in the `Info.plist` by adding an `extendedDescription` to the `QSPlugIn` section. This should be a string in HTML format.

If the plug-in project has been updated according to the [modernization section](#plugin_cleanup_and_modernization) below, keeping documentation up to date is as simple as editing (or creating) `Documentation.mdown` at the root of your project's repository (wherever `$SRCROOT` refers to). This is a Markdown file that should be much easier to deal with than raw HTML in Property List Editor.

It's processed using [Python-Markdown][pymd] with the [extra extension][mdex] enabled, so you can use the usual Markdown syntax, as well as tables, definition lists, etc.

If you need to refer to a Unix command, be aware of OS X's `x-man-page://` URL scheme. For example, linking to `x-man-page://ls` will open the man page for `ls` in a special Terminal window.

### Linking to Other Documentation ###

If in your plugin's Documentation, you want to link to the docs of another plugin, then use the relevant **full** URL from https://qsapp.com/manual/. E.g. to link to the E-Mail Support plugin's documentation, use the following URL: https://qsapp.com/manual/plugins/emailsupport/

### bltrversion ###

This script is called every time you build your project. A short explanation of what it does and the implications is in order. Every time you build, it will:

  1. Increment the Bundle version in `Info.plist`
  2. Convert `Documentation.mdown` to HTML and insert it into the `extendedDescription`

There are a couple of things to keep in mind.

  * It will not change the "short" version number that the user sees. You'll need to manage that manually.
  * The script unfortunately runs *after* the build, so if you want to update the version or documentation, you need to build, commit, then build again (and most likely revert the additional version bump that will result). This ensures that the built product matches what another developer will find in the repository.
  * Git will almost always show this file as having changed. Don't commit the change unless it's actually what you want.
  * You may have built the thing 250 times since the last commit, but do you really want the build number to jump that far when you were probably just testing some small changes? No. So either manually revert it to the last committed value, or increment it to something reasonable.
  * You can normally install an updated plug-in by double-clicking it in Finder, but it will only replace the old one if it has a higher build number. If you lowered the number recently in order to commit something more reasonable, you might have to manually remove the old version (with a higher build number) before you can install the latest.
  * Python and Objective-C programs unnecessarily escape quotes in property lists, while Property List Editor does not. So if you build to update the documentation, then commit, then make a small change via Property List Editor, you will see a large number of meaningless changes to `Info.plist`. One option is to just build again, reverting the HTML to the previous format.

[pymd]: http://packages.python.org/Markdown/
[mdex]: http://packages.python.org/Markdown/extensions/extra.html

## Property List Overview ##

Throughout this document are numerous references to things that go in a plug-in's property list. Refer back here if you want to see it all in one place.

### QSPlugIn ###

author (string)
: Put your name(s) here.

description (string)
: A one-line description of your plug-in's purpose.

extendedDescription (string)
: This is what the user will see when they click the Help (?) button in the Plugins section of the preferences. It can be text or HTML (recommended).

icon (string)
: This can be anything recognized by `-[QSResourceManager imageNamed:]`, which generally includes full paths, bundle IDs, or resources defined in various property lists. Other occurrences of `icon` in the property list follow this same convention.

categories (array)
: This is a list of categories you'd like the plug-in to be listed under. The full list of existing categories can be found under "All Plug-ins" in the Preferences.

hidden (boolean)
: This is generally only used by internal plug-ins bundled with Quicksilver. It's a boolean that tells whether or not your plug-in should show up on the list in the preferences.

relatedBundles (array)
: This is a list of bundle IDs for applications or plug-ins that are related. If a related bundle is present on the system, the plug-in will be listed in the "Recommended" section of the preferences.

relatedPaths (array)
: This is a list of paths for files or folders that might be related to your plug-in. This is useful for plug-ins based on some command-line tool(s) with no associated bundle. The path can be absolute, or use things like `~` to refer to the user's home directory. If a related file or folder is present on the system, the plug-in will be listed in the "Recommended" section of the preferences.

recommended (boolean)
: If a plug-in is likely to appeal to nearly everyone (such as Web Search), you can unconditionally add it to the "Recommended" section by setting this to `YES`.

webIcon (string)
: You can provide a URL that points to an image here.

### QSActions ###

The QSActions section contains an array of dictionaries. The key should be an internal identifier for your action, like `MakeStuffBetter`. Each action can have the following children.

name (string)
: The name the user will see (and search for) in the interface

description (string)
: A one-line description of what the action does. In interfaces that support it, this will appear in small text under the action's name.

commandFormat
: A sentence-like string that describes what's going to happen when you run the action. Enter `%@` as a placeholder for the direct object. For actions that take an indirect object, you can add a second placeholder. For example, "Move %@ to %@". In some cases, you might want to reverse the order of the two objects' names. That can be done by numbering them, as in "Search for %2$@ using %1$@".

icon (string)
: The image that will appear for this action in the interface

directTypes (array)
: A list of types this action applies to. It won't show up unless the object in the first pane has one of the types on this list.

directFileTypes (array)
: If one of your direct types is `NSFilenamesPboardType` (files), you can limit the types of files that match by providing a list of UTIs or extensions here.

indirectTypes (array)
: The types of objects that are allowed in the third pane (if this action uses it)

indirectOptional (boolean)
: Specifies whether or not the third pane is required

actionClass (string)
: The class that contains the method referred to by `actionSelector`

actionSelector (string)
: The method that does the work for this action. For instance, the `MakeStuffBetter` action might refer to a method called `makeStuffBetter:`. If the action takes an argument (like the name of a cute animal) in the third pane, you specify the name of the argument here as well, as in `makeStuffBetter:usingCuteAnimal:`.

reverseArguments (boolean)
: If true, the arguments will be sent to the `actionSelector` in the opposite order. Using the example above, an action that allowed cute animals in the first pane and something to make better in the third pane could reuse the `makeStuffBetter:usingCuteAnimal:` method you've already written.

alternateAction (String)
: The identifier of the alternate action

validatesObjects (Boolean)
: This tells Quicksilver whether or not to run `validActionsForDirectObject:`. That method gives you much more fine-grained control in cases where simply checking the type isn't sufficient to decide whether or not an action should be available.

displaysResult (Boolean)
: If true, the Quicksilver interface will reappear after your action runs, but only if your action returns a `QSObject`.

enabled (Boolean)
: Whether or not this action should be available by default when your plug in is installed for the first time

precedence (Number)
: A number between 0.0 and 4.0. A higher number means the action will rank higher in the 2nd pane. You should generally only use this if the action applies to a new type created by your plug-in, and not for any of the types Quicksilver knows of by default (especially files or text). Most of the built-in default actions have a low precedence and you can very easily overpower them here. Users would not appreciate this action suddenly becoming the default for files or text.

runInMainThread (Boolean)
: If true, this forces the action to be run in the main thread (for actions that interact some way with the user interface, you must set this to YES)

hidden (Boolean)
: Whether or not the action should be directly usable by the user. Hiding an action can be useful for example when you want to create an alternate action.

resolvesProxy (Boolean)
: By default, Quicksilver resolves proxy objects and passes the resulting "real" object on to the action. This prevents actions from having to test for and resolve proxies themselves. In rare cases, you might need to pass the proxy to an action as is. If so, set this to `NO`.

### QSRegistration ###

This section gives Quicksilver additional information about your plug-in.

#### QSTypeDefinitions ####

This allows your custom type(s) to appear in the Actions section of the preferences. Any new types provided by your plug-in should be described here. The key is the name of a type as defined in your code. Each entry should have two children: `name` and `icon`.

An optional key available starting in Quicksilver build 4012 is `smartspace`. The value for `smartspace` should be an integer from 1 to 6. (Set the type to "Number".) You only need to define this if the default smart spacebar behavior is undesirable for this type of object.

What is the default behavior?

  * If in the second pane, select the first action that takes an argument in the third pane
  * If user is holding Shift, go to the parent (same as left arrow)
  * If the object has children, show them (unless it's a text file)
  * Jump to the third pane if the current action requires it
  * Quick Look if the object supports it
  * Switch to text mode

The available override values and their behaviors are:

  * 1 - type a space
  * 2 - next result (act like down arrow or ⌃J)
  * 3 - jump to argument field (third pane)
  * 4 - switch to text-entry mode
  * 5 - show children (act like right arrow or slash)
  * 6 - Quick Look

#### QSBundleChildHandlers ####

This lists bundles that should have children provided by your plug-in. (Generally this is used to allow right-arrowing into an existing application like Mail or Address Book.) The key should be the bundle ID, and the value should be the name of a class that contains a `loadChildrenForObject:` method.

#### QSApplicationActions ####

These are actions that only appear when a specific application is in the first pane. The key should be the bundle ID of the application. Under this is a dictionary of actions. See the iTunes module for an example.

#### QSProxies ####

This defines proxy objects provided by the plug-in. Example:

    <key>QSProxies</key>
    <dict>
      <key>QSBlahProxyObject</key>
      <dict>
        <key>icon</key>
        <string>GenericDocument</string>
        <key>name</key>
        <string>Current Blah Thing</string>
        <key>providerClass</key>
        <string>QSBlahSource</string>
        <key>types</key>
        <array>
          <string>NSStringPboardType</string>
        </array>
      </dict>
    </dict>

Omitting the icon or setting its value to "ProxyIcon" will cause the proxy object to take on the icon of the resolved object.

#### QSTriggerEvents ####

Your plug-in can post notifications that can be used to signal an event trigger. In order to add these notifications to the Event Triggers pop-up menu, you need to define them here. `QSTriggerEvents` is a dictionary. Each key is the name of a notification. The value is another dictionary with these keys:

name
  : The name that will appear in the pop-up menu.
    
    For events generated exclusively by Quicksilver, you should add `☿` after the name. For example, the "File Tagged" event will not be detected when files are tagged in Finder; only when the tags are modified by a Quicksilver action. So the name is shown as "File Tagged ☿".

type
  : The category or group that this "event" will be under in the menu.

icon
  : The icon that will appear next to the item in the pop-up menu.

provider
  : The name of the class that posts the notification.

allowMatching
  : Whether or not the match/ignore controls for triggers using this event should be enabled. If you plan on passing something specific as the Event Trigger Object, this should probably be `YES`.

### QSPresetAdditions ###

This section defines catalog entries that should be available (but not necessarily active) by default under Plugins in the Catalog preferences. This can be a single entry, or a group with individual entries as children. Each object source has different options, so see the existing plug-ins for examples.

Note that the identifier for a preset should start with "QSPreset", especially if you define its `enabled` setting. If the identifier doesn't start with "QSPreset", it will fall back to the default you define for `enabled` on launch. In other words, you can never disable or enable these entries permanently.

### QSTriggerAdditions ###

This section defines triggers that should be added by default in the Triggers preferences. They should almost always be disabled by default.

### QSRequirements ###

You can define prerequisites and other restrictions for your plug-in. Most of these, if not met, will prevent an installed plug-in from loading, but many of them should tell the on-line update system not to even *offer* the plug-in in the user's list for installation.

minHostVersion (string)
  : The minimum version (build number) of Quicksilver required by this plug-in. Note: this replaces the now obsolete 'version (string)' key

maxHostVersion (string)
  : The maximum version (build number) of Quicksilver this plug-in will work with.

osRequired (string)
  : The minimum version of OS X required to use the plug-in. Use this to prevent the plug-in from loading on an older OS. You can write the version as `10.x.x` or just `10.x`.

    If you use this, you should also require Quicksilver build 4005 or higher, as older versions of Quicksilver will not respect the OS version restrictions.

osUnsupported (string)
  : The version of OS X at which this plug-in will stop working. Use this to prevent the plug-in from loading on a newer OS. You can write the version as `10.x.x` or just `10.x`.

    If you use this, you should also require Quicksilver build 4005 or higher, as older versions of Quicksilver will not respect the OS version restrictions.

plugins (array)
  : A list of dictionaries describing other plug-ins required by this one. For example:

        <key>plugins</key>
        <array>
          <dict>
            <key>id</key>
            <string>com.blacktree.Quicksilver.QSChatSupport</string>
            <key>name</key>
            <string>Chat Support</string>
          </dict>
        </array>

    These plug-ins will be installed automatically to support your plug-in.

bundles (array)
  : A more general list of things that must be installed before this plug-in will load. You can also require a minimum version of the bundle. For example:

        <key>bundles</key>
        <array>
          <dict>
            <key>id</key>
            <string>ch.sudo.cyberduck</string>
            <key>name</key>
            <string>Cyberduck</string>
            <key>version</key>
            <string>3.8</string>
          </dict>
        </array>

paths (array)
  : A list of strings defining files or folders that must exist for this plug-in to load.

frameworks (array)
  : Require specific frameworks and versions. For example:

        <key>frameworks</key>
        <array>
          <dict>
            <key>id</key>
            <string>com.skype.skypeframework</string>
            <key>name</key>
            <string>Skype Framework</string>
            <key>resource</key>
            <dict>
              <key>bundle</key>
              <string>com.skype.skype</string>
              <key>path</key>
              <string>/Contents/Frameworks/Skype.framework</string>
            </dict>
            <key>version</key>
            <string>0.1</string>
          </dict>
        </array>

obsoletes (array)
  : An array of bundle identifiers (strings) for plug-ins that are made obsolete by this one. For example:

        <key>obsoletes</key>
        <array>
          <string>com.blacktree.Quicksilver.QSAirPortPlugIn</string>
          <string>com.blacktree.Quicksilver.QSNetworkLocationPlugIn</string>
        </array>

    The update system will alert users with the obsolete plug-ins that your plug-in is available (and what it replaces). You could also use the `obsoletes` key to change the bundle identifier for an existing plug-in, but care should be taken in using it for this purpose.
  
    To use the `obsoletes` key, you should also require Quicksilver version 3926 or higher.

### QSResourceAdditions ###

You can define short names here to use with `QSResourceManager`. This is most useful to refer to icons buried inside a bundle somewhere (including your own plug-in's bundle). It can also be used to refer to the absolute path of an image file. For example:

    <key>QSResourceAdditions</key>
    <dict>
      <key>QSBlahImage</key>
      <dict>
        <key>bundle</key>
        <string>com.qsapp.QSBlah</string>
        <key>resource</key>
        <string>SomeImage.png</string>
      </dict>
      <key>QSBlahAnotherImage</key>
      <string>/Absolute/Path/to/an/Image.png</string>
    </dict>

Since icons have a history of moving around or disappearing with various OS X updates, you also have the ability to assign "fall back" values for each resource. Instead of referring directly to a dictionary or a string, refer to an array of them. You can mix strings and dictionaries. For example:

    <key>QSResourceAdditions</key>
    <dict>
      <key>QSBlahImage</key>
      <array>
        <dict>
          <key>bundle</key>
          <string>com.qsapp.QSBlah</string>
          <key>resource</key>
          <string>SomeImage.png</string>
        </dict>
        <string>/Absolute/Path/to/an/Image.png</string>
      </array>
    </dict>

The identifier for a resource defined here can be used as the value for any `icon` in the plist, and it can be used in code:

    [object setIcon:[QSResourceManager imageNamed:@"QSBlahImage"]];

<!-- TODO there's a lot more in the plist -->

## Actions ##

### Overview ###

To add an action, there are two basic steps:

  1. Define the action in `Info.plist`
  2. Write the action's code

You'll define your actions in the [`QSActions` section](#qsactions) of the property list.

    <key>QSActions</key>
    <dict>
        <key>someExmapleAction</key>
        <dict>
            <key>actionClass</key>
            <string>QSBlahActionProvider</string>
            <key>actionSelector</key>
            <string>performActionOnObject:</string>
            <key>directTypes</key>
            <array>
                <string>QSBlahType</string>
            </array>
            <key>name</key>
            <string>Blah Example Action</string>
        </dict>
    </dict>

That's the bare minimum. There are several additional keys described in the [Property List Overview](#property_list_overview).

For the code, you'll have something like this:

    - (QSObject *)performActionOnObject:(QSObject *)dObject
    {
        NSLog(@"I'm doing something with %@", [dObject stringValue]);
        id theMeat = [dObject objectForType:QSBlahType];
        return nil;
    }

An action that expects and object in the third pane will have an `actionSelector` like `performActionOnObject:withObject:` and the code will look more like this:

    - (QSObject *)performActionOnObject:(QSObject *)dObject withObject:(QSObject *)iObject
    {
        NSLog(@"Sending %@ to %@", [dObject stringValue], [iObject stringValue]);
        return nil;
    }

An action should **always** be defined to return a `QSObject`, even if it never needs to return anything. A `(void)` action will crash Quicksilver. Actions aren't typically defined in your action provider's header file, but they can be if it makes you more comfortable.

### Direct and Indirect Objects ###

You may see references to direct and indirect objects. Basically, direct objects are the things in the first pane of Quicksilver's interface and indirect objects are the thing in the third pane.

If you're looking at existing code, these are usually referred to as `dObject` and `iObject`. You don't have to use these names, but it will save you some typing if you plan to copy and paste a lot from examples.

### Displaying Results ###

Something to note about the `displaysResult` option in `Info.plist`: This only means that Quicksilver will pop the interface back up *if* your action returns a `QSObject` to it. If you have an action that may or may not return something to the interface, it appears to be safe to enable this.

Also note that if your action returns a `QSObject` to Quicksilver, that *will* become the thing in the first pane, whether the UI is re-displayed or not. If not, the user will see the object you returned the next time he invokes Quicksilver.

### Alternate Actions ###

Alternate actions are a very powerful feature of Quicksilver. When a user selects an action in the second pane, they can hit ↩ to run it, or they can hit ⌘↩ to run an alternate (if one is defined). Generally an alternate action will be similar to the main action, but modified in some way.

You create alternate actions just like any other action by adding a section for it in `Info.plist` and adding code in `BlahAction.m` for it. The main thing to note is that an action doesn't need to be active (checked in the preferences) to work as an alternate. You can define which of the actions in your plug-in are enabled or disabled by default, so an alternate could be something you never intend for the user to see/use directly or it could be one of the "normal" actions that you want to be conveniently accessible. Users can, of course, enable or disable actions themselves after your plug-in is installed.

Alternate actions should be able to take the same number of arguments as the main action. You can't define an alternate that requires something in the third pane for an action that doesn't use the third pane.

To define an alternate for an action, add an item named `alternateAction` to your action's properties in `Info.plist`. The value for `alternateAction` should be the identifier of another action.

### Reverse Actions ###

Some actions are reversible. For instance, web searches can be either

    Search Engine → Search For… → [search terms]

or

    [search terms] → Find With… → Search Engine

Reverse actions are added to the plist just like any other action. They should be more or less identical to the "forward" version of the action, with a couple of key changes:

  1. The identifier for the action should be different.
  2. The name of the action should be different.
  3. There should be a boolean called `reverseArguments` set to `YES`

### The Comma Trick ###

If you want your actions to support the comma trick (where a user can select several things in the first pane and act on them), you'll have to write actions to loop through all the objects and do the appropriate thing. If you expect to get several objects of the same type, the easiest technique involves getting a quick representation of each. `QSObject`s have several properties but you can specify which one should be associated with a specific type when the object is created using `setObject:forType:`. Assuming you set these as strings, you can get at them like this:

    for (NSString *userSelectedThing in [dObject arrayForType:QSBlahType])
    {
        // code
    }

Note that the above code will also work if the user just passes a single item to your action.

If you need to get the full details of the `QSObject`s passed in, you can do something like the following in your action's code:

    for (QSObject *individual in [dObject splitObjects])
    {
        NSString *thisGuy = [individual name];
        NSString *somethingWeNeed = [individual objectForMeta:@"key"];
    }

`splitObjects` is safe to use on single `QSObject`s, so it will work for any case, but sometimes you need to know which you have. The best way to tell if you're dealing with single vs. multiple objects is to look at the count:

    if ([dObject count] == 1)
    {
        // single object
    } else {
        // multiple objects
    }

For actions that won't support the comma trick, you should use the object validation process to prevent those actions from ever showing up, rather than checking for multiple objects in the action itself.

### Validating Objects ###

#### validActionsForDirectObject ####

Example: `- (NSArray *)validActionsForDirectObject:(QSObject *)dObject indirectObject:(QSObject *)iObject`

If you set `validatesObjects` to `YES` on an action in `Info.plist`, that action will never appear unless you add some corresponding code. This method must exist in `BlahAction.m` and return the identifier of any actions that you think will be safe to run based on whatever validation steps you've gone through. It should return an array of action names as strings. Perhaps you don't want the actions to work with strings longer than 100 characters or something. You could accomplish that with:

    NSString *myString = [[dObject arrayForType:QSBlahType] lastObject];
    NSMutableArray *newActions = [NSMutableArray arrayWithCapacity:1];
    if ([myString length] < 100) {
        [newActions addObject:@"FirstAction"];
        [newActions addObject:@"SecondAction"];
    }
    return newActions;

Keep in mind that Quicksilver has to run this validation code on every object that ever gets selected in the first pane in order to determine if this action is applicable or not before it can display the actions in the second pane. And not just for your plug-in. It's every validation method from every active plug-in every time a user selects something. It should go without saying at this point, but make sure your `validActionsForDirectObject:` method returns quickly!

#### validIndirectObjectsForAction

Example: `- (NSArray *)validIndirectObjectsForAction:(NSString *)action directObject:(QSObject *)dObject`

This method gets called when going to the third pane (for actions that provide one). It should return an array of `QSObject`s that are valid for that action. For instance, selecting a file and choosing the "Move To…" action will only show folders in the third pane.

To make sure the third pane comes up in text entry mode instead of regular "search" mode, do something like this:

    return [NSArray arrayWithObject:[QSObject textProxyObjectWithDefaultValue:@""]];

You can set the default text to whatever and that text will appear (selected) in the third pane. The above example just makes it blank.

If the third pane will ask for some sort of search text, you should stick to the convention of other plug-ins (and Mac OS X in general) and set the default text to be whatever the user last searched for. To accomplish that:

    NSString *searchString = [[NSPasteboard pasteboardWithName:NSFindPboard] stringForType:NSStringPboardType];
    return [NSArray arrayWithObject:[QSObject textProxyObjectWithDefaultValue:searchString]];

When you return a simple array, the first object will be selected by default. To select a specific object, return a two element array. The first element should be the object you want selected. The second element should be the entire list of possible objects. For example:

    QSObject *selectedThing = [indirectObjects objectAtIndex:4];
    return @[selectedThing, indirectObjects];

### AppleScript Actions ###

It's possible to define actions that exist only as AppleScript and not as Objective-C. These actions will look a little bit different in your `Info.plist`.

  1. `actionClass` should be set to "QSAppleScriptActions".
  2. `actionScript` should be set to the name of an AppleScript file, like "Blah.scpt". This script will need to be copied into your plug-in's `Resources` folder. A single AppleScript file can handle multiple actions (by using different `actionHandler`s).
  3. `actionHandler` should be the name of a function in the script, like "do_this_thing" (assuming the script has something like this in it).
     
        on do_this_thing(objectFromQuicksilver)
            tell application "XYZ" to lick the face of objectFromQuicksilver
        end do_this_thing

You'd omit the `actionSelector` for AppleScript actions.

I'm not sure what happens if you send multiple objects (via the comma trick) to an AppleScript action.

### Application Actions ###

*Applications Actions* are actions that only appear in the list of actions when a specific application if selected in the first pane of Quicksilver. Examples of this are the actions "Next Song", "Play - Pause", "Previous Song" that are provided by the iTunes plugin and only appear if iTunes is selected in the first pane. Or the "Get New Mail" and "Open New Mail" actions for Mail.app.

These actions are defined in the `Info.plist` of the plugin, in `QSRegistration` → `QSApplicationActions` → bundle identifier → action identifier. The same pattern can be used as in the normal actions (inside `QSActions`) **OR** a `QSCommand`. For an example of how `QSApplicationActions` are defined, see [the Info.plist of the Apple Mail Plugin](https://github.com/quicksilver/com.apple.Mail-qsplugin/blob/master/Info.plist).

## Commands ##

A `QSCommand` is something that contains a direct object, an action, and an indirect object. In other words, it encapsulates something you would normally put together in Quicksilver's interface.

Commands can be created by users (using the ⌃↩ "encapsulate" keystroke), by code (using methods from the `QSCommand` class), and in a plug-ins `Info.plist` (Under `QSRegistration` → `QSCommands`). Triggers refer to commands for obvious reasons.

One thing to note is that commands don't require either a direct or indirect object. For example, the iTunes plug-in comes with a number of predefined triggers like "Play", "Increase Volume", "Increase Rating", etc. These always do the same thing. There's no need to specify an object for them to act on. As a result, the commands these triggers refer to contain only an action.

When defining commands in the property list, the contents will vary greatly depending on the `actionID`. The `actionID` can refer to any action, but there are only a few that make sense. Below are examples of three common types.

For commands that call an Objective-C method somewhere, use "QSObjCSendMessageAction":

    <key>QSiTunesMute</key>
    <dict>
      <key>command</key>
      <dict>
        <key>actionID</key>
        <string>QSObjCSendMessageAction</string>
        <key>directArchive</key>
        <dict>
          <key>data</key>
          <dict>
            <key>qs.action</key>
            <dict>
              <key>actionClass</key>
              <string>QSiTunesControlProvider</string>
              <key>actionSelector</key>
              <string>volumeMute</string>
              <key>icon</key>
              <string>iTunesIcon</string>
              <key>name</key>
              <string>Mute</string>
            </dict>
          </dict>
        </dict>
        <key>directID</key>
        <string>QSiTunesVolumeMute</string>
      </dict>
    </dict>

**Be sure the key and `directID` are not the same.**

For commands that should invoke Quicksilver, and allow searching a specific subset of objects, use "QSObjectSearchChildrenAction":

    <key>QSiTunesSearchArtists</key>
    <dict>
      <key>command</key>
      <dict>
        <key>actionID</key>
        <string>QSObjectSearchChildrenAction</string>
        <key>directArchive</key>
        <dict>
          <key>data</key>
          <dict>
            <key>com.apple.itunes.qsbrowsercriteria</key>
            <dict>
              <key>Result</key>
              <string>Artist</string>
              <key>Type</key>
              <string>Artist</string>
            </dict>
          </dict>
        </dict>
      </dict>
      <key>name</key>
      <string>Search Artists</string>
    </dict>

For commands that are handled by an AppleScript file somewhere, use "AppleScriptRunAction":

    <key>QSiTunesMute</key>
    <dict>
      <key>command</key>
      <dict>
        <key>actionID</key>
        <string>AppleScriptRunAction</string>
        <key>directResource</key>
        <dict>
          <key>bundle</key>
          <string>com.blacktree.Quicksilver.QSiTunesPlugIn</string>
          <key>path</key>
          <string>Contents/Resources/Scripts/Mute.scpt</string>
        </dict>
      </dict>
    </dict>

## Trigger Presets ##

Your plug-in can provide pre-defined triggers. These go under `QSTriggerAdditions` and look something like this:

    <key>ID</key>
    <string>QSiTunesNextSongTrigger</string>
    <key>command</key>
    <string>QSiTunesNextSongCommand</string>
    <key>defaults</key>
    <dict>
      <key>characters</key>
      <string></string>
      <key>keyCode</key>
      <integer>124</integer>
      <key>modifiers</key>
      <integer>9961768</integer>
      <key>type</key>
      <string>QSHotKeyTrigger</string>
    </dict>
    <key>name</key>
    <string>Next Song</string>
    <key>set</key>
    <string>iTunes</string>

Only the type is required under `defaults` if you don't want to specify a shortcut. The `set` refers to the name of a group in the Trigger preferences. To create a new group for your plug-in's triggers, add something like this under `QSRegistration` → `QSTriggerSets`:

    <key>QSBlah</key>
    <dict>
      <key>icon</key>
      <string>GenericDocument</string>
      <key>name</key>
      <string>Blah</string>
    </dict>

## Adding to the Catalog ##

### Info.plist ###

There are two sections in `Info.plist` you should know about.

`QSPresetAdditions` is where you can list catalog entries that should be present by default when your plug-in is loaded. (These are the things you see in the "Modules" section of the Catalog.) These can be normal existing sources, like "QSFileSystemObjectSource" (a.k.a. File & Folder Scanner), or they can refer to a new source you define yourself.

If you want to see what these look like, open `~/Library/Application Support/Quicksilver/Catalog.plist` and look at the `customEntries` section. In fact, one easy way to create a catalog preset for your plug-in is to create it as a custom entry in Quicksilver, then copy/paste it from `Catalog.plist`. The only thing you may want to add by hand is an `icon`. You'd also change `sources` to something like `QSBlahSource` if you're defining your own.

The other important section in the `Info.plist` is `QSRegistration`. If you're creating your own source instead of using one of the built-ins, you'll need to add it here so Quicksilver will use it. You'll want to make sure there's a dictionary called `QSObjectSources`. Create an item under this and set both the name and value to the name of the class in `BlahSource.m` that provides the source, such as `QSBlahSource`.

Also under `QSRegistration` are some settings you'll need if you want users to be able to "right arrow" into things (which can also be done with '/'). You can use `QSBundleChildHandlers` to allow right arrowing into bundles and you use `QSObjectHandlers` to allow arrowing into objects created by plug-ins.

The thing you use `QSBundleChildHandlers` for is generally some application that's already on the system and related to your plug-in, but has no direct knowledge of, or support for Quicksilver. The left hand side should be a bundle identifier, like `com.apple.Finder` and the right hand side should be the name of a class in your plug-in that contains a `loadChildrenForObject:` method.

By default, Quicksilver will show an application's recent documents when right-arrowing. Don't override this without good reason.

`QSObjectHandlers` tells Quicksilver where to go for more information about a particular type. This is typically a type that you've defined, but doesn't have to be. On the left should be a type of object in Quicksilver and on the right should be the name of a class in your plug-in that contains methods like `loadChildrenForObject:`, `setQuickIconForObject:`, etc. It might look like this:

    <key>QSObjectHandlers</key>
    <dict>
        <key>QSBlahType</key>
        <string>QSBlahSource</string>
        <key>QSBlahAnotherType</key>
        <string>QSBlahSource</string>
    </dict>

Note that you can use the same "source" class for all types, or create a separate class for each one. If you use the same source, the methods will just have to figure out what type of object they have before proceeding.

### Code ###

There are some methods you'll want to define in `BlahSource.m` and Quicksilver will call them at the appropriate time. This is not a complete list of available methods, but the common ones are covered. You can look at existing plug-ins for some example code. Note that many of these methods are only called by Quicksilver if you define something for `QSObjectHandlers` in `Info.plist`.

The information for an entry (from `Info.plist`) can be pulled in like this:

    NSMutableDictionary *settings = [theEntry objectForKey:kItemSettings];

Again, existing plug-ins can give you some examples of how to use this info since the dictionary contents can vary widely from one source to another.

#### objectsForEntry

Example: `- (NSArray *)objectsForEntry:(NSDictionary *)theEntry`

This method does the work of adding your objects to the catalog. It can do whatever you want it to do (parse files, get information over the network, query a database, etc.) as long as it returns an array of `QSObject`s.

There are several ways to create a `QSObject`. Here are a couple:

    QSObject *myObject = [QSObject objectWithString:string];
    QSObject *myObject = [QSObject objectWithName:name];
    QSObject *myObject = [QSObject URLObjectWithURL:url];

There is a full list of all the methods available for creating objects in the [Creating](#creating) section of this reference.

There are also things you may want to do to your objects prior to adding them to the array to be returned, like `setIdentifier:`, `setLabel:`, `setDetails:`, `setName:`, `setObject:forType:` etc. There's a whole section in this document on `QSObject` that provides more details.

#### indexIsValidFromDate

Example `- (BOOL)indexIsValidFromDate:(NSDate *)indexDate forEntry:(NSDictionary *)theEntry`

Quicksilver runs this during scheduled catalog updates (every 10 minutes by default) to ask "Is this catalog entry still up to date?" How you determine the answer to this question is up to you. If this method returns `YES`, Quicksilver moves along without doing anything. If this method returns `NO`, Quicksilver will attempt to update the entry by calling the `objectsForEntry:` method.

You can have this method do nothing but return `YES` or `NO` unconditionally, and that's exactly what it does for many plug-ins. Just keep in mind that this will either cause your source to never get updated (except manually) or cause it to get updated on every single rescan (which may be a performance concern, depending on what it does).

`indexDate` and `theEntry` are passed in by Quicksilver. The `indexDate` tells you when the entry was last updated in the catalog. `theEntry` contains information about the entry that you might need (file paths, URLs, etc.).

**NOTE**: This method is not consulted when your plug-in is first installed or when a user selects the entry in the catalog and hits the "rescan" button manually. In other words, if you're checking for errors with your source here to avoid unnecessary rescans, that's good, but you still need to check for errors in `objectsForEntry:` as well, because it will be called at least once.

To rescan your entry when a file has changed been changed since the last scan:

    - (BOOL)indexIsValidFromDate:(NSDate *)indexDate forEntry:(NSDictionary *)theEntry
    {
        // use the plist settings to determine which file to check
        NSMutableDictionary *settings = [theEntry objectForKey:kItemSettings];
        NSString *sourceFile = [self fullPathForSettings:settings];
        // get the last modified date on the source file
        NSFileManager *manager = [NSFileManager defaultManager];
        if (![manager fileExistsAtPath:sourceFile isDirectory:NULL]) return YES;
        NSDate *modDate = [[manager attributesOfItemAtPath:sourceFile error:NULL] fileModificationDate];
        // compare dates and return whether or not the entry should be rescanned
        if ([modDate compare:indexDate] == NSOrderedDescending) return NO;
        // if we fall through to this point, don't rescan by default
        return YES;
    }

To scan the entry once when Quicksilver starts, but never again:

    - (BOOL)indexIsValidFromDate:(NSDate *)indexDate forEntry:(NSDictionary *)theEntry {
        // rescan only if the indexDate is prior to the last launch
        NSDate *launched = [[NSRunningApplication currentApplication] launchDate];
        if (launched) {
            return ([launched compare:indexDate] == NSOrderedAscending);
        } else {
            // Quicksilver wasn't launched by LaunchServices - date unknown - rescan to be safe
            return NO;
        }
    }

In the above example, if Quicksilver relaunched itself (instead of being launched at login or via Finder), the `launchDate` will be unavailable, which is why you need to test the result.

#### setQuickIconForObject

Example: `- (void)setQuickIconForObject:(QSObject *)object`

If you call `setIcon:` when adding objects to the catalog, they will show up at first but quickly disappear. Calling `setIcon:` from this method instead will work more reliably. Example:

    [object setIcon:[QSResourceManager imageNamed:@"GenericNetworkIcon"]];

Quicksilver calls this in real-time as objects need to be displayed, which is why it appears more reliably. (It's probably more efficient that way too, compared to storing an icon for everything in the catalog whether it gets used or not.)

As the name implies, you should only use this for icons that are ready to display quickly. Generally, that means icons or images that are already in memory or on a fast, local disk. If you need to do anything more expensive, like generate a Quick Look preview, add a badge to the icon, or fetch an image over the network, do it in `loadIconForObject:`.

#### loadIconForObject

Example: `- (BOOL)loadIconForObject:(QSObject *)object`

This method is optional. After the "quick icon" has been set with `setQuickIconForObject:`, Quicksilver will ask your object source if it has this method, and if so, run it on a background thread.

This is where you should do more expensive image processing or fetching. If you end up with a valid image, you should call `setIcon:` again from here. If an icon already exists for the object, the main interface and results list will redraw the icon to reflect the change.

Some examples might be helpful.

  * The filesystem object source uses this method to replace the generic icon for files (based on type) with a Quick Look preview.
  * The URL object source replaces the generic URL icon on web searches with one that has the magnifying glass and favicon from the site overlaid.
  * The iTunes plug-in fetches album covers and video previews (via Quick Look) and uses them to replace the generic icon for those types.

#### loadChildrenForObject

Example: `- (BOOL)loadChildrenForObject:(QSObject *)object`

This is very similar to `objectsForEntry:`, but instead of adding things to the catalog, it loads them on the fly when you right arrow into the parent object. You just need to create an array of `QSObject`s, but instead of returning them, you assign them to the parent object like this:

    [object setChildren:children];
    return TRUE;

These can be newly created objects or objects that are already in the catalog. If the children have already been added to the catalog, the most efficient thing to do is to retrieve them instead of recreating them. (See the later sections on getting specific objects by ID and by type.)

**Read up on identifiers in the QSObject section before creating/using objects as children.**

#### objectHasChildren

Example: `- (BOOL)objectHasChildren:(QSObject *)object`

This method is used to indicate to the user that an object is browsable (can be right arrowed into). If it returns `YES`, a little arrow is displayed on the very right of the object.

If you used `loadChildrenForObject:` so the user can right arrow into an object, you should indicate that to the user by having this method return `YES`.

**NOTE**: Returning `NO` (or leaving this method out) will hide the little arrow indicator, but the user will still be able to arrow into the object if you provided children for the object by using `loadChildrenForObject:`.

#### isVisibleSource

Example: `- (BOOL)isVisibleSource`

This method determines whether or not your source shows up on the drop-down list for adding new custom catalog entries.

Return `NO` to keep this off of the drop-down. Return `YES` if you want users to be able to add custom entries of this type to their catalog. Keep in mind that you will also need to provide them with some sort of interface to do so.

See [Object Source Preferences](#object_source_preferences) for details.

<!-- TODO explain how to invalidate an entry (force a rescan)
### Forcing an Immediate Rescan ###
-->

### Actions ###

If the direct object is irrelevant, you can add actions directly to the catalog. They will appear in the first pane with a default action of "Run" in the second pane. Here's an example of creating a `QSAction` programatically.

    NSDictionary *actionDict = [NSDictionary dictionaryWithObjectsAndKeys:
        @"QSBlahActionProvider", kActionClass,
        @"doSomething", kActionSelector,
        @"BlahIcon", kActionIcon,
        @"Do Something", @"name",
        nil];
    
    newObject = [QSAction actionWithDictionary:actionDict
        identifier:@"QSBlahDoSomething"
        bundle:nil];

You could have that in your `objectsForEntry:` method and add `newObject` to the array it returns.

## Custom Types ##

You may want to add a new type of thing to Quicksilver's catalog that doesn't conform to the existing types Quicksilver knows about. The main reason you'd want to do this is to make your actions apply only to relevant entries. For instance, you may want "SSH to host" as the default for remote hosts. Though hostnames and FQDNs are just strings and can be added to Quicksilver easily, simply adding them to the catalog as strings would cause the default action to be "Open URL" or "Large Type" in most cases. You would either have to choose the SSH action manually every time, or move it up in priority making it the default for all text and URLs, which probably isn't what you want.

### Source ###

To use a custom type when adding objects to the catalog, the first thing to do is add something like this to one of your header files:

    #define QSBlahType @"blah.specific.type"

You'll probably want to use this in your action code too, so many plug-ins define things like this in a dedicated file, rather than in the object source.

Then, in your `objectsForEntry:` method in `BlahSource.m`, you would do something like this on each QSObject before adding it to the array:

    [myObject setObject:someValue forType:QSBlahType];

Now, when you're adding actions to the `Info.plist`, they can use "blah.specific.type" as a value under `directTypes` or `indirectTypes`. You will almost certainly want to assign other types in addition to the one you've created. See "Types" in the QSObject section for details.

### Actions ###

Speaking of actions, if your action(s) need to refer to your custom type, you should include the header where the type is defined, then in the various action methods in `BlahAction.m`, you can test for objects of that type with something like this:

    if ([dObject containsType:QSBlahType]) {}

This allows you to use code completion and reduce the chance for typing errors. Unfortunately, whenever you refer to the types in your property list, you need to use the actual string the type refers to.

## QSObject ##

Your plug-in will communicate with Quicksilver pretty much entirely through `QSObject` objects. That is, Quicksilver will send `QSObject`s to your methods, and if you need to send something back to Quicksilver, you'll return either a single `QSObject` or an array of them. Here are some details on creating them and using those previously created.

### Creating ###

You'll need to create `QSObject`s if adding things to the catalog and also if your action needs to send something back to Quicksilver (to end up in the first pane of the UI). This section is largely written with adding to the catalog in mind, but the information should be useful for returning objects for display as well (because it's so dead simple by comparison). There are several methods for creating new `QSObject`s. Here are some of the most common.

  * objectWithString
  * objectWithName
  * makeObjectWithIdentifier
  * objectWithURL
  * fileObjectWithPath

`objectWithName:` simply creates an empty object and stores the name in the object's dictionary of metadata. `objectWithString:` will use the string to set the name, but it also sets the type to `QSTextType` and then does some fancy analysis (using QSObject (StringHandling)'s `sniffString` method) to figure out if the string should be treated differently in any way. This is how strings can be turned into URL objects or file objects automagically. Also of note: The Mac OS X spell checker has no problem with "automagically".)

Most of the time, you probably want to take advantage of Quicksilver's "smarts" and use `objectWithString:` but if for some reason you just want it to take your string and not mess with it, use `objectWithName:`.

In my experience, you don't need to do anything more than the above to create a usable object, but you will probably want to add more details such as…

#### Identifier ####

An identifier for your `QSObject` isn't required, but I recommend always setting one. In any case, it's important to understand how they're used. You set one like this:

    [myObject setIdentifier:someString];

In addition to actually storing the identifier string in your object, this causes Quicksilver to add the object to an internal registry.

If you choose an identifier that is already in use, you will **replace the existing object** with your new one in the registry. This has a couple of implications. First, you should obviously pick a unique string to use as an identifier. Second, if you end up "recreating" various objects (either to appear in the third pane, or to act as children for another object) be careful what you do with them. Here are some tips:

  1. For objects that just serve some temporary purpose in the UI, add a prefix to the identifier, or don't even set one.
  2. Wherever possible, use existing objects instead of recreating identical ones.
  3. If you want to use an existing object, but modify it in some way, create a new empty `QSObject` and assign it attributes from the existing object as needed.

#### Name ####

If you've created an object using one of QSObject's more 'basic' methods such as `objectWithIdentifier:` or even `[[QSObject alloc] init]` it is important to set the object's name using the `setName:@"some name"` method.

This is the most prominent string in the UI (unless you set a label), and Quicksilver matches against it when a user is typing.

#### Label ####

This is optional, but if you want the text that appears most prominently in the user interface to be something other than the name, you can set this using `setLabel:@"some string"`.

This is also the string that Quicksilver matches against when a user is typing, so keep that in mind. You can make things easier for users to find in the catalog by messing with the label. (The name will still be searchable as well, and will appear instead when matched.)

If you set name and label to the same thing, the value will be set as the name and the label will be removed automatically.

#### Type ####

To set a type for an object, do something like this:

    [myObject setObject:someObject forType:QSBlahType];

A `QSObject` can have multiple types, so you can call this method multiple times, each with a different type, if you want. That deserves some further discussion. Most actions in Quicksilver only work with certain types. You will probably want to make built-in actions or actions defined in other plug-ins do something useful with your objects, which may be of a new type Quicksilver has never heard of. The "Paste" and "Large Type" actions are prime examples. You can't very well expect various other plug-ins (or Quicksilver itself) to add support for your new type. This is where you want to use an existing type to get things working.

Hopefully, by now, you've figured out what the object is supposed to be for each type you assign. It will be something that actions supporting that type can make use of. (See the warning on arrays below.) I'll use "Paste" as an example. The "Paste" action works with a few types I'm sure, but the simplest one is `QSTextType`. The thing you want to paste in that case will be a string. Your `QSObject` probably has many strings (name, label, details, etc.) so how can you tell Quicksilver which to spit out when running the "Paste" action? Like this:

    [myObject setObject:thisString forType:QSTextType];

Now, when a user selects this object and uses an action that works with `QSTextType`, it will use `thisString`.

If you set multiple types, you should also set one as primary.

    [myObject setPrimaryType:QSBlahType];

Don't use `setPrimaryType:` alone. You must also call `setObject:forType:` using the same type at some point.

Here are all the types Quicksilver declares in `QSTypes.h`. Examples of their creation and use are available in existing code.

    QSFilePathType
    QSTextType
    QSAliasDataType
    QSAliasFilePathType
    QSURLType
    QSEmailAddressType
    QSContactEmailType
    QSContactPhoneType
    QSContactAddressType
    QSFormulaType
    QSActionType
    QSProcessType
    QSMachineAddressType
    QSABPersonType
    QSNumericType
    QSIMAccountType
    QSIMMultiAccountType
    QSPasteboardDataType
    QSCommandType
    QSHandledType

A warning about arrays: If you call `[object setObject:someArray forType:QSBlahType]` then call `[object objectForType:QSBlahType]`, you will only get the array's last object. To get the original array back, call `[object arrayForType:QSBlahType]` instead.

#### Details ####

The "details" string is the text that appears smaller underneath the label in most Quicksilver interfaces. Set it using `setDetails:@"some string"`.

Setting this explicitly is optional but if you don't, Quicksilver will pick something. In some cases, it uses the identifier. Keep this in mind if your identifiers aren't very nice to look at.

#### Icon ####

You can set an icon (as an `NSImage`) for a `QSObject` using the `setIcon:` method. Quicksilver makes it easy go get various images with `QSResourceManager`. Just do something like this:

    [myObject setIcon:[QSResourceManager imageNamed:@"GenericNetworkIcon"]];

I don't recommend using the `setIcon:` method when adding things to the catalog. (See the note on `setQuickIconForObject:` for an explanation.) However, using this method directly from one of your actions does work if you want to set the icon temporarily for something you're sending back to the Quicksilver UI. (That too will go away, but this is only an issue if the user leaves the object you return up in the first pane.)

FYI, if you want to use one of the standard system icons for something, many can be found in `/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources`. You can refer to them using only the file's name (no path and no ".icns" extension). To use the icon for an application, use its bundle identifier, like `com.apple.Mail`. Finally, you can also provide the full path to an image file. Here are some examples:

    [QSResourceManager imageNamed:@"com.apple.Mail"]
    [QSResourceManager imageNamed:@"/Users/me/Pictures/Some.icns"]

You can also use `QSResourceManager` to get specific icons from inside a bundle's Resources folder, but that requires a bit of extra work. For example, to use the bookmark menu icon in Safari's bundle, you need to define a section in the property list called `QSResourceAdditions`, then define different icons under it, such as:

    <key>SafariBookmarkMenuIcon</key>
    <dict>
      <key>bundle</key>
      <string>com.apple.Safari</string>
      <key>resource</key>
      <string>tiny_menu.tiff</string>
    </dict>

That will allow you to refer to the icon in your code with something like

    [QSResourceManager imageNamed:@"SafariBookmarkMenuIcon"]

Finally, if you want to use the icon for a particular file type, here's one method using the extension.

    NSImage *pdfIcon = [[NSWorkspace sharedWorkspace] iconForFileType:@"pdf"];
    [myObject setIcon:pdfIcon];

#### Children ####

Usually, you'll load and set children on-the-fly using `loadChildrenForObject:`, but it does seem to be possible to set them when an object is first created as well. Assuming you have created an array of other `QSObject`s called "children", you can set them like this:

    [myObject setChildren:children];

These child objects will appear in the UI if a user select your object and hits → or /.

#### Parent ####

If you have set children for an object so you can right arrow into them, these children should also know about their parent object. This builds a proper hierarchy and helps QS to figure out what to do when you arrow back out of the list of children objects (using ←).

So, before using `[myObject setChildren:children]` to set children for an object, for each of the children `QSObject`s, you should set the parent ID to the identifier of the parent `QSObject`. For example by doing the following for each `QSObject` in the `children` array:

    [childObject setParentID:[myObject identifier]];

Then, once the user arrows back out of the list of children, the correct object will be selected in the main QS pane and also be highlighted in the result list.

<!-- TODO imho this should be done automatically inside the setChildren method, but that isn't done right now :-/ -->

#### Arbitrary Metadata ####

In addition to the standard things like name, label, icon, and type, `QSObject`s provide a metadata dictionary. You can store just about anything in here, so the possibilities for your plug-in get really interesting with this. If your objects are files, perhaps you want to store their size here. Perhaps you want to store width, height, and resolution for an image. Maybe you want to store a thumbnail image for the object. (It doesn't have to be a string.) Perhaps you just like to waste memory on other people's computers and want to store the lyrics to your favorite song.

To add your custom metadata to the object, you would do something like:

    [myObject setObject:value forMeta:@"key name"];

The key name is just a string you'll use to refer to this thing in the dictionary later. The value can by any type of object.

There'll be more on this in the next section. As a real-world example, one use I found for this was customizing icons for things in the catalog. As mentioned elsewhere, using `setIcon:` when things are added to the catalog is the wrong approach. You could probably store the icon as metadata, but this is inefficient. A better approach is to just store some identifying string as metadata, and move the logic that uses that data over to the `setQuickIconForObject:` method.

### Using ###

When Quicksilver passes `QSObject`s to your actions, here are some of the ways to get information out of them.

#### String Values ####

To get a quick string representation of an object for whatever reason:

    NSString *blah = [dObject stringValue];

This is probably best for objects you didn't create and don't know the contents of. The `stringValue` method tries do do some smart things, but if none that pans out, it will call `displayName`. The `displayName` method will return the label if set, otherwise it returns the name.

If you're familiar with what an object contains and you want to get the name or label specifically, you can use `[dObject name]` or `[dObject label]`.

#### Metadata ####

To retrieve metadata that you may have set when adding objects to the catalog:

    id value = [dObject objectForMeta:@"key name"];

Of course you if you know the type of object, you can be more specific than `id`.

This metadata has many possibilities, but two of the more obvious are:

  1. Checking to see which actions will work on this object (using `validActionsForDirectObject`)
  2. Directing the behavior of your actions

#### "combined objects" ####

If a user sends multiple things to your action using the comma trick, then `[dObject stringValue]` will return "combined objects". I give examples of how to loop through one of these combined objects in the Actions section.

#### Getting Specific Objects by ID ####

The `objectWithIdentifier:` method will return an existing `QSObject` if you know what it's ID was set to (probably because you set it yourself). It's a class method, so you don't call it on any particular object.

    QSObject *thisGuy = [QSObject objectWithIdentifier:uuid];

If building plug-ins for build 4008 or higher, you should get objects from `QSLibrarian` instead.

    QSObject *thisGuy = [QSLib objectWithIdentifier:uuid];

As a general rule, this will only work for objects that have been added to the catalog. It might work for other objects if they were recently used and are still in memory.

#### Getting Specific Objects by Type ####

You can use `QSLibrarian` to retrieve objects from Quicksilver's catalog by type. The most common uses for this are to restrict the objects that appear in the third pane, and to build up a list of children for another object.

To simply get everything of a certain type, call this:

    NSArray *objects = [QSLib arrayForType:@"QSBlahType"];

To get the same list but sort by rank (typically determined by how often a user accesses the object):

    NSArray *objects = [QSLib scoredArrayForType:@"QSBlahType"];

#### Respecting Disabled Objects ####

Users have the ability to remove individual objects from the catalog by unchecking them in the source entry's preferences. When providing a list of children or objects in the third pane, it's generally appropriate to respect these disabled objects and prevent them from appearing.

If you pull existing objects from the catalog by type as described above, the objects should already be omitted in build 4008 or later. If you're using an older build, getting a list by calling `objectForEntry:`, or generating objects on-the-fly somehow, you'll need to omit these items from the results yourself.

Here's one possible way to do it:

    // unfilteredResults is the array you start from
    NSIndexSet *enabled = [unfilteredResults indexesOfObjectsWithOptions:NSEnumerationConcurrent passingTest:^BOOL(QSObject *obj, NSUInteger idx, BOOL *stop) {
        return ![QSLib itemIsOmitted:obj];
    }];
    NSArray *filteredResults = [unfilteredResults objectsAtIndexes:enabled];

### More Information ###

A lot can be figured out by looking through `QSObject.m`. If you really want to track down *everything* `QSObject` provides, search for "@implementation QSObject" in the Quicksilver source and stare in horror at the number of results.

## Proxy Objects ##

The property list entry that defines a proxy object is discussed above. See [`QSProxies`](#qsproxies). The `providerClass` defined in the plist should conform to the `QSProxyObjectProvider` protocol. The most important method there is `resolveProxyObject:`.

This method is responsible for returning the "real" object referred to by one or more proxies. If the class is only responsible for one proxy object, it usually returns an object blindly, but if it handles more than one, it needs to see which (usually by checking the identifier) before returning a value.

    - (QSObject *)resolveProxyObject:(QSProxyObject *)proxy
    {
        NSString *ident = [proxy identifier];
        if ([ident isEqualToString:@"QSBlahExampleProxy"]) {
            QSObject *resolved = nil;
            // do work to figure out what this object currently refers to
            return resolved;
        }
        return nil;
    }

There are other optional methods you can implement in the `providerClass` for proxy objects.

Proxies are often requested multiple times in rapid succession, so Quicksilver tries to avoid resolving them every time. You can control the amount of time a proxy will hold onto its current value before doing the work of resolving it again. The default is 3 seconds. 0 is not recommended, but might make sense when the value of the object is already in memory.

    - (NSTimeInterval)cacheTimeForProxy:(id)proxy
    {
        return 10.0;
    }

If the types for your proxy object are known in advance, just define them in the plist. Some proxy objects may refer to different types of `QSObject`s in different contexts. (Think about "Current Selection".) The type can be set dynamically to ensure that the correct actions appear in the second pane.

    - (NSArray *)typesForProxyObject:(QSProxyObject *)proxy
    {
        // figure out which types apply
        // return an array of type names (strings)
    }

There are other methods you can implement to dynamically assign details, icons, etc., but these aren't specific to proxy objects.

### Current Selection ###

If you're working on a plug-in for a specific application, you can often improve the behavior of Quicksilver's built-in "Current Selection" proxy object.

When a user asks for Current Selection, Quicksilver will first see if any plug-ins claim to know how to get a selection from the front-most application (based on its bundle identifier). If not, it will simply tell the application to "Copy" and hope the pasteboard contains something useful.

To claim support for a particular application, define a proxy object like any other, but use the application's bundle ID as the proxy object's identifier in the plist.

Note that when Quicksilver looks up this proxy and finds the provider class, it will send `[provider resolveProxyObject:nil]`. You might want to put the selection business in a dedicated class so you don't have to worry about what value was passed in. You can just blindly return the selection in that case.

If the Current Selection proxy is handled by the same class as other proxy objects, you'll need to do some testing to figure out if Current Selection is the one being requested. iTunes and iPhoto do something like this:

    if (!proxy || [[proxy identifier] isEqualToString:@"com.apple.iTunes"])

Why would you put other proxies in the same class with Current Selection? Because Current Selection only applies to the front-most application. Many useful triggers depend on getting the selection from a specific application, whether it's active or not, so you're probably also going to define a "Current Blah Selection" for that. You don't want to duplicate the code for getting the selection in two different classes, so you'll have to put them in the same place.

## Preferences ##

This is a rough outline of what you need to do to add a preference pane for your plug-in.

  * add a new user interface file with a single window
  * uncheck Visible At Launch in the Attributes inspector
  * uncheck Release When Closed in the Attributes inspector
  * add a class to your project such as `QSBlahPrefPane` that inherits from `QSPreferencePane`
  * set File's Owner to be `QSBlahPrefPane`
  * connect the window to `_window` on File's Owner
  * add something like this to the plist under `QSRegistration`:
  
        <key>QSPreferencePanes</key>
        <dict>
            <key>QSBlahPrefPane</key>
              <dict>
                  <key>class</key>
                  <string>QSBlahPrefPane</string>
                  <key>name</key>
                  <string>Blah Blah Blah</string>
                  <key>description</key>
                  <string>Preferences</string>
                  <key>icon</key>
                  <string>QSBlahImage</string>
              </dict>
        </dict>
  
  * add your controls to the window and bind them to the right preferences (Shared Preferences Controller → values → QSBlahSetting)

   **Note:** You can create clickable href-links to your preference pane using the format `qs://<MyPreferencePaneClass>` that link directly to your preference pane. E.g. if your preference pane class is called `QSBlahPrefPane`, the link `qs://QSBlahPrefPane` will take you directly to your preference pane. This can be useful for linking users to the preference pane from websites, or opening the preference pane from within your plugin using `[[NSWorkspace sharedWorkspace] openURL:[NSURL UrlWithPath:@"qs://QSBlahPrefPane"]];`

## Object Source Preferences ##

  * add a new user interface file with a single view
  * uncheck Use Auto Layout in the File inspector
  * set File's Owner to `QSBlahSource`
  * bind File's Owner `settingsView` to the new view
  * create controls and bind them to outlets/actions in File's Owner
  * add a strings file to the project called `QSObjectSource.name.strings` (or set the name as the key under `QSObjectSources` if it won't be localized)

You'll need to add at these methods to `QSBlahSource`.

Make this source appear on the drop-down for adding new catalog entries:

    - (BOOL)isVisibleSource
    {
        return YES;
    }

Return the icon that will appear next to the source name in the drop-down and next to custom entries:

    - (NSImage *) iconForEntry:(NSDictionary *)theEntry
    {
        // this can be smarter based on theEntry - up to you
        return [QSResourceManager imageNamed:@"GenericDocument"];
    }

Load your custom view:

    - (NSView *)settingsView
    {
        if (![super settingsView]) {
            [NSBundle loadNibNamed:NSStringFromClass([self class]) owner:self];
        }
        return [super settingsView];
    }

Update the view every time the selection changes:

    - (void)populateFields
    {
        NSMutableDictionary *settings = [[self currentEntry] objectForKey:kItemSettings];
        // set values for controls in the view based on settings
    }

To customize the name of the source in the drop-down, add something like this to the `strings` file:

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>QSBlahSource</key>
    	<string>Blah Source</string>
    </dict>
    </plist>

And of course you need to make sure you update or create the catalog entry when changes are made in the interface. See `QSFileSystemObjectSource` for an example.

## Event Triggers ##

Any plug-in can define additional "events" to be monitored by the Event Triggers plug-in. There are a couple of reasons you might post a notification from a plug-in:

  1. Your plug-in does something that takes a long time. Particularly if it does it in the background.
  2. The result of some command might be useful in a follow-up command. (More on the Event Trigger Object later.)
  3. Your plug-in does something atypical *automatically* in the background.

To set this up correctly, you need an entry in `Info.plist` and some code to post the notification. A typical property list entry looks like this:

    <key>QSBlahThingHappened</key>
    <dict>
    	<key>name</key>
    	<string>Operation Finished ☿</string>
    	<key>icon</key>
    	<string>IconName</string>
    	<key>provider</key>
    	<string>QSBlahSource</string>
    	<key>type</key>
    	<string>Blah</string>
    </dict>

See [QSTriggerEvents](#qstriggerevents) for details.

Posting the notification should look something like this:

    NSDictionary *info = @{@"object": someQSObject};
    [[NSNotificationCenter defaultCenter] postNotificationName:@"QSEventNotification" object:@"QSBlahThingHappened" userInfo:info];

The object passed with the notification should be a string matching the key name defined in the property list.

`userInfo` can be `nil`, but if you pass anything, it should be a dictionary containing a `QSObject` for the key "object". The Event Triggers plug-in includes a proxy object called "Event Trigger Object". You can use that in an event trigger to refer to the `QSObject` included in `userInfo`. This potentially allows for powerful combinations of commands.

If you don't pass anything, the Event Trigger Object will just be a string object based on the event's name.

## Scripting Bridge ##

If you plan to use the Scripting Bridge in your plug-in, here are some tips.

In addition to the steps from [Getting Started](#getting_started), you'll need two more things in your project:

  1. The Scripting Bridge framework
  2. A header file describing the capabilities of the application you want to script

The framework is included with OS X and can be added like any other. For the header file, there are two ways to proceed: Generate the file and add it to the project, or have the file generated automatically when you build the plug-in.

The automatic way means you'll always have the latest header if something changes, but it's more complicated to set up, it makes searching the project more difficult, and you may get changes you didn't want.

Both methods are described here. Choose only one.

### Adding the Header Manually ###

To create the header file, you'll want to run `sdef` on the application in question, then pipe its output to `sdp` and define a base name for all the classes. (The base name is usually the application's name with no whitespace.)

For example, to create a header for scripting Safari:

    sdef /Applications/Safari.app  | sdp -fh --basename Safari

This will create `Safari.h` in the current directory. Add that file to your plug-in project in Xcode, and you'll be able to import it from any one of your files.

### Generating the Header During Build ###

  1. Drag the application(s) you want scripting support for into your project. Don't let it copy the files.
  2. Use the Utilities panel to change the location for each application to "Absolute Path".
  3. Select the project on the left, then select the target (under TARGETS) on the right.
  4. Open the "Build Phases" tab.
  5. Drag the application(s) to the "Compile Sources" section and make sure it's the first thing on the list.
  6. Go to the "Build Rules" tab.
  7. Add a new build rule, set Process to "Source files with names matching" and enter `*.app`
  8. Select "Custom script" and enter this command:
  
        sdef "$INPUT_FILE_PATH" | sdp -fh -o "$DERIVED_FILES_DIR" --basename "$INPUT_FILE_BASE"	--bundleid `defaults read "$INPUT_FILE_PATH/Contents/Info" CFBundleIdentifier`
  
  9. Add an output file with the path `$(DERIVED_FILES_DIR)/$(INPUT_FILE_BASE).h`
  10. Add a line to import the resulting header file to the appropriate header files in your project. For example, if you added Safari, you'd enter:
  
        #import "Safari.h"
        
      This file won't exist until you build for the first time.

### Overview ###

Scripting Bridge is typically an excellent way to get information from an application, but a terrible way to control it. Unfortunately, for Quicksilver you basically need the opposite.

Keep in mind at all times that in order to interact with an application via Scripting Bridge, the application must be running. As a result, you should not use it to add objects to the catalog. Users will not appreciate applications launching seemingly at random (when Quicksilver updates the catalog entry). You need to find another way to get the same info (typically by parsing files on disk somewhere).

The type of objects Scripting Bridge is appropriate for is real-time items from an application, like "currently playing track", or "all open tabs". In most cases such as this, you should check `[appname isRunning]` before trying to get the information.

When defining actions on the other hand, it's generally OK to blindly interact with the application. For instance, if the user wants to play a track, it makes sense to open iTunes if it isn't already running.

### Performance ###

I won't try to repeat what's in the [official documentation][sbdoc], but you should look it over. It's not very long. In particular, see the sections on Using Element Arrays and improving performance. The general rule is: Minimize the number of Apple Events.

Having said that, there are exceptions I've run across, so you might have to get creative.

### Weirdness ###

There are some strange things you're going to run across. Here are some known examples.

#### get ####

You generally don't need to call `get` on an `SBObject` or `SBElementArray`… except when you do. My advice is to avoid it unless something that seems like it should work just isn't working. Then add a call to `get`. One known example is when trying to use FourCharCodes in an `NSPredicate`. This should work, but doesn't:

    NSArray *iTunesDJplaylists = [[library playlists] filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"specialKind == %i", iTunesESpKPartyShuffle]];

This works:

    NSArray *iTunesDJplaylists = [[[library playlists] get] filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"specialKind == %i", iTunesESpKPartyShuffle]];

If the predicate just uses strings, it seems to work fine without `get`. Huh?

#### SBElementArray ####

An `SBElementArray` (according to the documentation) is just an `NSMutableArray` and can be treated like one… except when it can't (which of course is *not* documented). In my experience, you can remove all objects or remove specific ones, but adding objects is problematic. It almost never works, but when it does, it seems to require something like

    [array insertObject:newThing atIndex:0];

My only advice is to start searching the web for answers when you get into this situation.

[sbdoc]: http://developer.apple.com/library/mac/#documentation/Cocoa/Conceptual/ScriptingBridgeConcepts/Introduction/Introduction.html

## Troubleshooting ##

When testing a newly built plug-in, if things don't work as expected, don't go back to the code looking for the problem right away. It may be that you're testing against cached data from older code. This process seems to ensure that you're actually testing your latest build.

  1. Install the newly built plug-in
  2. Relaunch Quicksilver
  3. Rescan the catalog entries for your plug-in
  4. Relaunch Quicksilver again

If the problem is actually with the plug-in, try these steps.

  1. Check for mistakes in the plist
  2. Check for mistakes in the plist
  3. Check for mistakes in the plist

Repeating that was not a typo. If you're convinced that the problem isn't there, take a step back for a few minutes. Maybe, while you have some time to kill, you could go over everything in the plist *again*. :-)

If it won't build at all

  1. If you're doing a Debug build, make sure you've recently built Quicksilver using the Debug configuration. (Files should be in `/tmp/QS/build/Debug`.) Same for Release builds.
  2. Try cleaning with ⇧⌘K

If you're trying to work on one of the existing plug-ins and you can't get it to build, here are a couple of things that have worked for me.

  1. Build Quicksilver from source (Release, not Debug). The process puts a lot of things in `/tmp/QS/build/Release/` that the source for the plug-ins expect to find there.
  2. Make sure the plug-in is using the `.xcconfig` files and that there aren't any incorrect build settings in the local project that override them.
  3. In the File Inspector, make sure the paths are correct. (They will sometimes be pointing to a previous developer's home directory.)
  4. Tell Xcode to do a "Release" build of the plug-in instead of "Debug". (I'm not sure what all the ramifications are with this, but it seems to work.)

### Debugging Plug-ins ###

To be able to debug plugins using an actual debugger instead of just `NSLog()` statements, there are a few steps that need to be done. Some of these steps are already described in the **Getting Started** section in the beginning of this guide, just check again to make sure everything is set up correctly.

#### From the Plug-in ####

  1. Build Quicksilver using the Debug configuration
  2. Go to Product → Edit Scheme… (⌘<)
  3. Select the project's Debug configuration
  4. Set the executable to `/tmp/QS/build/Debug/Quicksilver.app`
  5. Remove the plug-in from `~/Library/Application Support/Quicksilver/PlugIns` (if installed)

Now, as long as you're using the Debug configuration, you should be able to set breakpoints inside the plug-in code itself.

#### From Quicksilver ####

  1. Build Quicksilver using the Debug configuration
  2. Build your plug-in using the Debug configuration
  3. Install your plug-in to `~/Library/Application Support/Quicksilver/PlugIns`. (If it has a higher build number than the current plug-in, double-clicking it should be sufficient. Otherwise, you'll need to manually remove the current copy of the plug-in.)
  4. Go back to the Quicksilver project in Xcode
  5. Go to the Breakpoint Navigator (⌘6)
  6. Set a symbolic breakpoint for a method in your plug-in, such as `-[QSBlahSource objectsForEntry:]`
  7. Run Quicksilver from Xcode (⌘R) using the Debug configuration
  8. Do whatever is necessary to trigger the method you want to trace

Note that even with no breakpoints set, the debugger will take you into your plug-in's code if any exceptions are encountered. This sounds quite complicated, but once you have set it up correctly, debugging is pretty straight forward: Build plugin, install plugin, debug Quicksilver.

## Plug-in Clean-up and Modernization ##

There are a few things we've been doing to every plug-in we update. If you're working on an existing plug-in, please go through this check list and make sure it's in good shape.

  1. Make sure the project is correctly set up to use Quicksilver's `.xcconfig` files
      * Look at the `Configuration` folder in the File Inspector. Make sure it's set as an "Absolute Path" and that the path is `/private/tmp/QS/Configuration` (The "full path" won't include `/private` and that's fine.)
      * Under the `Configuration` folder, remove references to `QSPlugIn_Release.xcconfig` and `QSPlugIn_Debug.xcconfig` (if they exist). They're not necessary with Xcode 4.
      * Select the project in the Project Navigator then go to the project's "Info" tab. Under Configurations, you should see "Debug" and "Release". The project under each should be based on "Debug" or "Release" respectively, and the target under each should be based on "QSPlugIn".
      * Go through the build settings for both the project and the target. As a general rule, nothing should be in bold. Select anything that's bold and hit Delete.
      * Optionally enable Automatic Reference Counting. (This is likely to be the default in Quicksilver's `.xcconfig` files soon.)
  2. Use the shared copy of `bltrversion`
      * Go to the target's "Build Phases" tab.
      * Drag the "Run Script" phase for `bltrversion` as high as you can (it should be 2nd on the list).
      * Change the content of the script to `"$QS_BUILD_ROOT/Tools/bltrversion"`
      * Update the name from "Run Script" to something useful, like "Update Version and Documentation"
  3. Remove redundant `#import` statements. Most of the headers the plug-ins depend on are taken care of by `Quicksilver.pch`. Go through all of the project's files and remove any references to headers from the OS or from Quicksilver. This isn't a complete list, but some common ones are `Cocoa.h`, `Carbon.h`, `Foundation.h`, `QSCore.h`, `QSPlugIn.h`, `QSActionProvider.h`, and `QSObjectSource.h`.
  4. Remove any unused files from the plug-in's Git repository and from the Xcode project. If the code is still inside a `trunk` folder, move it up a level and get rid of `trunk`.
  5. Update the `Info.plist`
      * Add "Bundle versions string, short" and set it to something like 1.0.0
      * Add "Bundle display name". This name will have the type (Quicksilver Plugin) appended to it, so it shouldn't necessarily match the Bundle name. For example, if the display name is "Blah Plugin", it will show up as "Blah Plugin Quicksilver Plugin", so keep it simple.
      * Remove unused or obsolete keys (QSPlugIn → qsversion, QSRequirements → level)
      * Set the executable name to `${EXECUTABLE_NAME}`. This should make it automatically match the Product Name from the target.
  6. Look for any references to "module" or "plug-in" and change them to "plugin". Even though "plug-in" is correct, the community has elected to go another way, so keep it consistent.
  7. Update the code for 64-bit. The specifics are well documented elsewhere, so I'm not going to cover it here.
  8. Last but not least, **make sure the plug-in has adequate documentation** for end-users.

## Links ##

Some things that might help.

[Developer Information from QSApp.com](http://qsapp.com/wiki/Developer_Information) - From the official wiki.

[The Existing Plug-ins](http://github.com/quicksilver) - Loads and loads of undocumented, uncommented examples that you may or may not be able to make sense of.

[The Remote Hosts Module](https://github.com/quicksilver/RemoteHosts-qsplugin) - Not to plug my own work, but it's the only frakking plug-in I've seen with a single frakking comment to explain what's going on, so it might be worth a look.

[The iTunes Plug-in](https://github.com/quicksilver/iTunes-qsplugin) - Almost everything that's possible (and a couple of things that aren't) are done by this plug-in, so it's a good reference.

[Some information on setting up a project for Scripting Bridge](http://robnapier.net/blog/scripting-bridge-265)
