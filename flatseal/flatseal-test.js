imports.gi.versions.Gio = '2.0';
imports.gi.versions.Gtk = '4.0';
imports.gi.versions.Adw = '1';
imports.gi.versions.WebKit = '6.0';

const {Gio, GLib} = imports.gi;
const System = imports.system;
const resourceDirectory = '/app/share/flatseal';

const resources = [
    'com.github.tchx84.Flatseal.data.gresource',
    'com.github.tchx84.Flatseal.src.gresource',
];
for (const resource of resources)
    Gio.Resource.load(`${resourceDirectory}/${resource}`)._register();
imports.searchPath.unshift('resource:///com/github/tchx84/Flatseal/js');

const localeDirectory = GLib.getenv('FLATSEAL_TRANSLATION_DIR');
if (!localeDirectory)
    throw new Error('FLATSEAL_TRANSLATION_DIR is not set');

const gettext = imports.gettext;
gettext.bindtextdomain('flatseal', localeDirectory);
gettext.textdomain('flatseal');
globalThis._ = gettext.gettext;
globalThis.C_ = gettext.pgettext;
globalThis.N_ = value => value;

imports.package.initFormat();
imports.package.require({
    Gio: '2.0',
    Gtk: '4.0',
    Adw: '1',
    WebKit: '6.0',
});

const {FlatsealApplication} = imports.application;
if (ARGV[0] === '--check-translation') {
    print(gettext.gettext('Flatpak Version'));
    System.exit(0);
}

const application = new FlatsealApplication();
System.exit(application.run([System.programInvocationName, ...ARGV]));
