#encoding:utf8
from flask import Flask, request, render_template, abort
import git
import markdown
import json
import codecs
import shutil
import os
import zipfile
import tarfile

app = Flask(__name__)
app.debug = True

doc_save_to = os.path.join(os.path.split(app.instance_path)[0], 'docs')
if not os.path.isdir(doc_save_to):
    os.makedirs(doc_save_to)

app.config.from_pyfile('main.cfg')

@app.route('/', methods=['GET', 'POST'])
def doc_builder():
    #print request.args.get('payload')
    payload = request.form['payload']
    json_payload = json.loads(payload)
    repo_name = json_payload['repository']['name']
    config = doc_config(repo_name)
    if len(config):
        return 'NOT configure docs generater for this repo'
    before_commit = json_payload['before']
    after_commit = json_payload['after']
    doc_parser(config)
    return "Hello Document!"

@app.route('/docs/<string:repo>/<path:path>')
@app.route('/docs/<string:repo>/')
def doc_viewer(repo, path='index.html'):
    #print request.path
    #os.makedirs('/tmp/a/s/d')
    doc_file = os.path.join('static', repo, path)
    doc_file = os.path.join('/tmp/doc_builder.git/docs', path)
    print doc_file
    if os.path.isfile(doc_file):
        return render_template(doc_file)
    else:
        abort(404)

def doc_config(repo):
    config = {
        'azeroth-server':{
            'name':'azeroth-server',
            'doc_path':'docs',
            'branch':'master',
            'url':'git@forfun.dev:azeroth-server.git',
            'theme':'default'
        },
        'browser':{
            'name':'browser',
            'doc_path':'docs',
            'branch':'master',
            'url':'git@forfun.dev:browser.git',
            'theme':'default'
        },
        'axoa':{
            'name':'axoa_dev',
            'doc_path':'docs',
            'branch':'develop',
            'url':'git@forfun.dev:axoa.git',
            'theme':'default'
        }
    }
    if config.has_key(repo):
        ret = config[repo]
    else:
        ret = {}
    return ret

@app.route('/down_zip/<string:repo>')
def doc_packager_zip(repo):
    tmp_dir = '/tmp/view_gen_tmp/'
    tmp_dir = doc_save_to
    tmp_dir = os.path.join(doc_save_to, name)
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    newfile = zipfile.ZipFile('azeroth.zip', mode='w', compression=zipfile.ZIP_DEFLATED)
    for item in os.listdir(tmp_dir):
        if not os.path.isdir(os.path.join(tmp_dir, item)):
            #print os.path.join(tmp_dir, item)
            name_in_arch = tmp_dir.lstrip(tmp_dir)
            newfile.write(os.path.join(tmp_dir, item), arcname=os.path.join(name_in_arch, item))
        #elif os.path.isdir(tmpdir+item):
        #    self.z(tmpdir+item+'/', newfile)
    newfile.close()

@app.route('/down_tar/<string:repo>')
def doc_packager_tar(repo):
    with tarfile.open("sample.tar.gz", "w:gz") as tar:
        for item in os.listdir('./axoa'):
            tar.add(os.path.join('./axoa', item))

def doc_parser(config, a=None, b=None):
    #docs dir eq
    doc_save_to = os.path.join(os.path.split(app.instance_path)[0], 'docs')
    #sure docs dir
    if not os.path.isdir(doc_save_to):
        os.makedirs(doc_save_to)
    #sure repo docs dir
    tmp_dir = os.path.join(doc_save_to, config['name'])
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    #sure repo git tmp dir
    tmp_path = os.path.join('/tmp/doc_builder', config['name'])
    #if os.path.isdir(tmp_path):
    #    shutil.rmtree(tmp_path)
    if not git.repo.fun.is_git_dir(os.path.join(tmp_path, '.git')):
        if os.path.isdir(tmp_path):
            shutil.rmtree(tmp_path)
        repo = git.Repo.init(tmp_path)
        origin = repo.create_remote('origin', config['url'])
    else:
        repo = git.Repo(tmp_path)
        origin = repo.remotes.origin
    try:
        origin.pull(config['branch'])
    except:
        pass
    repo.git.checkout(config['branch'])
    tree = repo.heads[config['branch']].commit.tree
    index_content = []
    for item in tree[config['doc_path']].blobs:
        #item.mime_type == 'text/plain'
        #item.size > 0
        splited = os.path.splitext(item.name)
        if (splited[1] == '.md'):
            path = os.path.split(item.abspath)
            rel_path = os.path.split(item.path)
            doc_rel_file = os.path.relpath(item.abspath, os.path.join(repo.working_dir, config['doc_path']))
            href = os.path.join(os.path.split(doc_rel_file)[0], splited[0] + '.html')
            index_content.append('<a href="' + href + '">'+ splited[0] +'</a><br>')
            save_path = os.path.join(path[0], splited[0] + '.html')
            if not os.path.isdir(os.path.join(doc_save_to, config['name'])):
                os.makedirs(os.path.join(doc_save_to, config['name']))
            save_path = os.path.join(doc_save_to, config['name'], splited[0] + '.html')
            content = tree[item.path].data_stream.read()
            content = content.decode('utf8')
            #safe_mode='replace',
            html = '<link href="markdown.css" rel="stylesheet"><link href="prettify.css" rel="stylesheet"><script src="prettify.js"></script>' + markdown.markdown(content, output_format='html5', extensions=['extra', 'toc'])
            output_file = codecs.open(save_path, 'w', encoding="utf-8", errors="xmlcharrefreplace")
            output_file.write(html)
            print '>> generated ' + item.name
    with open(os.path.join(os.path.join(doc_save_to, config['name']), 'index.html'), 'w') as fp:
        fp.writelines(index_content)
        print '>> generated index.html'

if __name__ == '__main__':
    config = doc_config('axoa')
    doc_parser(config)
    #app.run('0.0.0.0')

'''
TODO:
1.整理代码
2.剥离配置
3.增量更新，代码已有此逻辑，但需要找出remote方法不能执行的原因
4.提供主题
5.语法高亮
6.tar打包
'''
