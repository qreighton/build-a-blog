#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import re
import os
from google.appengine.ext import db


# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

#def get_posts(limit,offset):
#    return db.GqlQuery("Select * from Dblog Order by created Desc limit "+limit+" offset "+offset)

class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

class Dblog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
class MainPage(Handler):
    def render_front(self,title="",blog="",error=""):
        self.render("add.html",title = title,blog = blog,error = error)
    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")
        id = self.request.get("id")
        if title and blog:
            a = Dblog(title = title, blog = blog)
            a.put()
            id = a.key().id()
            id = str(id)
            self.redirect("/blog/"+id)
        if id:
            self.redirect("/blog/"+id)
        else:
            error ="we need a title and a blog"
            self.render_front(title,blog,error)
class Readblog(Handler):
    def render_front(self,title="",blog="",b=""):
        blogs = db.GqlQuery("Select * from Dblog Order by created Desc Limit 5")
        #blogs = get_posts(limit,offset)
        self.render("read.html",title = title,blog = blog,blogs = blogs)
    def get(self):
        self.render_front()
    def post(self):
        id = self.request.get("id")
        if id != "":
            id=str(id)
            self.redirect("/blog/"+id)
        else:
            self.redirect("/")
class ViewPostHandler(Handler):
    def get(self,id):

        b=""
        key=""
        if id.isdigit() ==True:
            id=int(id)
            b = Dblog.get_by_id(id,parent = None)
            if b != None:
                key = b.key().id()
                error =""
                self.render("one.html",error=error,b=b,key=key)
            else:
                error = "There is no blog with that id"
                self .render("one.html",error=error,b=b,key=key)
        else:
            b=None
            error = "There is no blog with that id"
            self .render("one.html",error=error,b=b,key=key)

    def post(self,id):
        id = self.request.get("id")
        self.redirect("/blog/"+id)
class BlankLine(Handler):
    def get(self):
        self.redirect("/blog/1")
    def post(self):
        self.redirect("/blog/1")
#I was messing with the hacker problem set but didnt have time to finish
#class ReadAll(Handler):
#    def get(self):
#        page=self.request.get("page")
#        limit="";offset="";offset2=""
#        if page:
#            limit=self.request.get("limit")
#            offset=self.request.get("offset")
#            self.front_page(page,limit,offset,offset2)
#        self.render("readall.html",title="",blog="",blogs="",pageup="soon",pageback="",limit=limit,offset=offset,error="",offset2=offset2)
#    def front_page(self,page,limit,offset,offset2):
#        if limit<1:
#            error="limit and offset need to be more than zero"
#            self.render("readall.html",title="",blog="",blogs="",pageup="buba",pageback="",limit=limit,offset=offset,error=error,offet2=offset2)
#        if page:
#            limit=int(limit)
#            offset2=int(offset2)
#            page=int(page)
#            offset2=offset2+(page*limit)
#            offset2=(offset2*limit)
#            limit=str(limit)
#            offset2=str(offset2)
#        blogs=get_posts(limit,offset2)
#        p =blogs.count()
#        pageup="pageup"
#        pageback="pageback"
#        if int(p)<=int(offset):
#            pageup =""
#        if int(offset)=="0":
#            pageback =""
#        self.render("readall.html",title="",blog="",blogs=blogs,
#                                   pageup=pageup,pageback=pageback,
#                                   limit=limit,offset=offset,p=p,
#                                   error="",offset2=offset)
#    def post(self):
#        page="";
#        limit=self.request.get("limit")
#        offset=self.request.get("offset")
#        offset2=self.request.get("offset2")
#        if offset2<offset:
#            offset2=offset
#        self.front_page(page,limit,offset,offset2)



app = webapp2.WSGIApplication([
    ('/', Readblog),('/newpost',MainPage),
    ('/blog/',BlankLine),webapp2.Route('/blog/<id:\S+>', ViewPostHandler)

],debug=True)
