#encoding=utf8
import git
import markdown
import codecs
import os
import shutil

'''
{
    "repository": {
        "url": null,
        "owner": {
            "name": "lizaifang",
            "email": "lizaifang@gmail.com"
        },
        "name": "azeroth-server",
        "description": ""
    },
    "commits": [{
        "url": null,
        "timestamp": "2013-09-06T11:07:35+0800",
        "message": "    test hookt",
        "id": "8c8542f97a5c74eb5e42a84fcab97b26e6acfb94",
        "author": {
            "name": "lizaifang",
            "email": "lizaifang@gmail.com"
        }
    }],
    "after": "8c8542f97a5c74eb5e42a84fcab97b26e6acfb94",
    "action": "mod_master",
    "ref": "refs/heads/master",
    "before": "feb35a53c5d20d430aecd3a74519a15ea610468d"
}
{
    "repository": {
        "url": "git@forfun.dev:azeroth-server.git",
        "owner": {
            "name": "lizaifang",
            "email": "lizaifang@gmail.com"
        },
        "name": "azeroth-server",
        "description": ""
    },
    "commits": [{
        "url": "git@forfun.dev:azeroth-server.git/commit/acd37cd8cfd370d56be91fad1f78bc70b7852c32",
        "timestamp": "2013-09-06T11:12:52+0800",
        "message": "    test hookt",
        "id": "acd37cd8cfd370d56be91fad1f78bc70b7852c32",
        "author": {
            "name": "lizaifang",
            "email": "lizaifang@gmail.com"
        }
    }],
    "after": "acd37cd8cfd370d56be91fad1f78bc70b7852c32",
    "action": "mod_master",
    "ref": "refs/heads/master",
    "before": "8c8542f97a5c74eb5e42a84fcab97b26e6acfb94"
}
'''

branch = 'master'
branch = 'develop'
doc_path = 'docs'

class GitProgress(git.remote.RemoteProgress):
  def setKey(self, _id):
    self._id = _id
  
  def update(self, op_code, cur_count, max_count=None, message=''):
    db = pymongo.Connection().giuseppe
    db.clone_status.save({
      "_id": self._id,
      "op_code": op_code,
      "cur_count": cur_count,
      "max_count": max_count
    })

class Rp(git.remote.RemoteProgress):
    def __init__(self):
        pass
    def line_dropped(self, line):
        print line
    def update(self, op_code, cur_count, max_count=None, message=''):
        print op_code, cur_count, max_count, message


oldmask = os.umask(022)
os.umask(0)
repo = git.Repo('/home/project/33-oa/ci.axoa')
print repo.remotes.origin.url
#rp = Rp()
rp = git.remote.RemoteProgress()
if os.path.isdir('/tmp/axoa'):
    print shutil.rmtree('/tmp/axoa')
repo.clone('/tmp/axoa', progress=rp)
repo = git.Repo('/tmp/axoa')
print repo.remotes.origin.url

#repo = git.Repo.init(tmp_path)
#origin = repo.create_remote('origin', 'git@forfun.dev:azeroth-server.git')

repo = git.Repo('/home/project/33-oa/ci.axoa')

repo.git.checkout('develop')
repo.heads[branch].checkout() 
print repo.commit(branch).size
print len(list(repo.iter_commits(branch)))
tree = repo.heads[branch].commit.tree
print tree[doc_path]
print tree[doc_path].blobs
print tree[doc_path].trees
for item in tree[doc_path].blobs:
    #print item.mime_type
    #print item.abspath
    #print item.name
    #print item.size
    splited = os.path.splitext(item.name)
    if (splited[1] == '.md'):
        path = os.path.split(item.abspath)
        save_path = os.path.join(path[0], splited[0] + '.html')
        content = tree[item.path].data_stream.read()
        content = content.decode('utf8')
        #safe_mode='replace',
        html = '<link href="markdown.css" rel="stylesheet"><link href="prettify.css" rel="stylesheet"><script src="prettify.js"></script>' + markdown.markdown(content, output_format='html5', extensions=['extra', 'toc'])
        output_file = codecs.open(save_path, 'w', encoding="utf-8", errors="xmlcharrefreplace")
        output_file.write(html)
        print '>> generated ' + item.name

a = repo.commit('7bc063a4c7a776a6a580ba5a6f032c75c69b32a2')
b = repo.commit('fd649f98dd084ca28dbcfead6cff55414b7bb977')
diff = a.diff(b)
for diff_added in diff.iter_change_type('M'):
    print(diff_added.a_blob.path)
    print(diff_added.a_blob.name)
    #print(diff_added.b_blob.data_stream.read())
for diff_added in diff.iter_change_type('A'):
    print(diff_added.a_blob.path)
for diff_added in diff.iter_change_type('R'):
    print(diff_added.a_blob.path)
for diff_added in diff.iter_change_type('D'):
    print(diff_added.a_blob.path)

print repo.is_dirty()
print repo.untracked_files
print repo.archive(open('/tmp/repo.tar.gz', 'w'))
os.umask(oldmask)
#git archive -o ../updated.zip HEAD $(git diff --name-only HEAD^)

'''
~~~~{.python}
# python code
~~~~

~~~~.html
<p>HTML Document</p>
~~~~

{.html #example-1}
<pre class="prettyprint"><code class="language-html">...</code></pre>
<pre class="prettyprint lang-html">

http://pythonhosted.org/Markdown/reference.html
http://pythonhosted.org/Markdown/extensions/index.html


Extension	"Name"
Extra	extra
    Abbreviations	abbr
    Attribute Lists	attr_list
    Definition Lists	def_list
    Fenced Code Blocks	fenced_code
    Footnotes	footnotes
    Tables	tables
    Smart Strong	smart_strong
Admonition	admonition
CodeHilite	codehilite
HeaderId	headerid
Meta-Data	meta
New Line to Break	nl2br
Sane Lists	sane_lists
Table of Contents	toc
WikiLinks
'''

