#!/usr/bin/env python
import os
import stat
import md5
import re
import zipfile
import tempfile
import shutil
from xml.dom import minidom
from ConfigParser import SafeConfigParser

class main:
    def __init__(self):
        self.config = SafeConfigParser()
        self.config.read("config.ini")
        self.tools_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
        self.output_path = "pages/repo/"
        
        # travel path one up
        self.path_ad = os.path.abspath(os.path.join(self.tools_path, os.pardir))
        os.chdir(self.path_ad)

        # generate files
        self._pre_run()
        self._generate_addon_files()
        self._generate_repo_files()
        self._generate_md5_file()
        self._generate_zip_files()
        # notify user
        print "Finished updating addons xml, md5 files and zipping addons"

    def _pre_run(self):
        # create output  path if it does not exists
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def _generate_addon_files(self):
        repo_urls = self.config.items("addons")
        if len(repo_urls) == 0:
            print "No addons in config.ini"
        else:
            try:
                global git
                import git
            except ImportError:
                raise RuntimeError("Need GitPython")
            for repo_url in repo_urls:
                self._git_clone(repo_url[0], repo_url[1])
                shutil.rmtree('_temp')

    def _git_clone(self, name, url):
        # Parse the format "REPOSITORY_URL#BRANCH:PATH". The colon is a delimiter
        # unless it looks more like a scheme, (e.g., "http://").
        match = re.match('((?:[A-Za-z0-9+.-]+://)?.*?)(?:#([^#]*?))?(?::([^:]*))?$', url)
        (clone_repo, clone_branch, clone_path_option) = match.group(1, 2, 3)
        clone_path = './' if clone_path_option is None else clone_path_option
        temp_path = '_temp/' + name
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        try:
            # Check out the sources.
            cloned = git.Repo.clone_from(clone_repo, temp_path)
            if clone_branch is not None:
                cloned.git.checkout(clone_branch)
            clone_source_folder = os.path.join(clone_path)
            shutil.copytree(temp_path + '/' + clone_source_folder, (self.path_ad + os.path.sep + name))
        finally:
            shutil.rmtree(temp_path, onerror=del_rw)
            print (name + " done")

    def _generate_repo_files(self):
        # addon list
        addons = os.listdir( "." )
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        for addon in addons:
            # create path
            _path = os.path.join( addon, "addon.xml" )
            #skip path if it has no addon.xml
            if not os.path.isfile( _path ): continue
            try:               
                # split lines for stripping
                xml_lines = open( _path, "r" ).read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ): continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "utf-8" )
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
        self._save_file( addons_xml.encode( "utf-8" ), file=self.output_path + "addons.xml" )

    def _save_file(self, data, file):
        try:
            # write data to the file
            open( file, "w" ).write( data )
        except Exception, e:
            # oops
            print "An error occurred saving %s file!\n%s" % ( file, e, )

    def _generate_md5_file(self):
        try:
            # create a new md5 hash
            m = md5.new( open(self.output_path +  "addons.xml" ).read() ).hexdigest()
            # save file
            self._save_file( m, file=self.output_path + "addons.xml.md5" )
        except Exception, e:
            # oops
            print "An error occurred creating addons.xml.md5 file!\n%s" % ( e, )

    def _generate_zip_files(self):
        addons = os.listdir( "." )
        # loop thru and add each addons addon.xml file
        for addon in addons:
            # create path
            _path = os.path.join( addon, "addon.xml" )         
            #skip path if it has no addon.xml
            if not os.path.isfile( _path ): continue       
            try:
                # skip any file or .git folder
                if ( not os.path.isdir( addon ) or addon == ".git" or addon == self.output_path or addon == self.tools_path): continue
                # create path
                _path = os.path.join( addon, "addon.xml" )
                # split lines for stripping
                document = minidom.parse(_path)
                for parent in document.getElementsByTagName("addon"):
                    version = parent.getAttribute("version")
                    addonid = parent.getAttribute("id")
                self._generate_zip_file(addon, version, addonid)
            except Exception, e:
                print e

    def _generate_zip_file(self, path, version, addonid):
        print "Generate zip file for " + addonid + "-" + version
        filename = path + "-" + version + ".zip"
        try:
            zip = zipfile.ZipFile(filename, 'w')
            for root, dirs, files in os.walk(path + os.path.sep):
                for file in files:
                    zip.write(os.path.join(root, file))
                    
            zip.close()
         
            if not os.path.exists(self.output_path + addonid):
                os.makedirs(self.output_path + addonid)
         
            if os.path.isfile(self.output_path + addonid + os.path.sep + filename):
                os.remove(self.output_path + addonid + os.path.sep + filename )
            shutil.move(filename, self.output_path + addonid + os.path.sep + filename)
            shutil.move(path + os.path.sep + 'icon.png', self.output_path + addonid + os.path.sep + 'icon.png')
            shutil.move(path + os.path.sep + 'fanart.jpg', self.output_path + addonid + os.path.sep + 'fanart.jpg')
            shutil.copy(path + os.path.sep + 'changelog.txt', self.output_path + addonid + os.path.sep + 'changelog.txt')
            shutil.move(path + os.path.sep + 'changelog.txt', self.output_path + addonid + os.path.sep + 'changelog-' + version +'.txt')
        except Exception, e:
            print e

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

if __name__ == "__main__":
    main()
