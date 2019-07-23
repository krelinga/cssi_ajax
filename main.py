# Copyright 2016 Google Inc.
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

import webapp2
import jinja2
import os
import json

from google.appengine.api import users
from google.appengine.ext import ndb

def root_parent():
    '''A single key to be used as the ancestor for all dog entries.
    Allows for strong consistency at the cost of scalability.'''
    return ndb.Key('Parent', 'default_parent')

class UserNote(ndb.Model):
    user = ndb.UserProperty()
    note = ndb.StringProperty()

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = JINJA_ENVIRONMENT.get_template('templates/main.html')
        data = {
          'user': user,
          'login_url': users.create_login_url('/'),
          'logout_url': users.create_logout_url('/'),
        }
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(data))

def GetUserNote(user):
    '''Queries datastore to get the current value of the note associated with this user.'''
    notes = UserNote.query(UserNote.user == user, ancestor=root_parent()).fetch()
    if len(notes) > 0:
        # We found a note, return it.
        return notes[0]
    else:
        # We didn't find a note, return None
        return None

class UpdateNote(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = JINJA_ENVIRONMENT.get_template('templates/update_note.html')
        user_note = None
        if user is not None:
            # There is a logged-in user, so try to look up their current note.
            user_note = GetUserNote(user)
        data = {
          'user': user,
          'login_url': users.create_login_url('/update_note'),
          'logout_url': users.create_logout_url('/update_note'),
          'user_note': user_note,
        }
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(data))

    def post(self):
        user = users.get_current_user()
        if user is None:
            # No user is logged in, so don't allow any changes.
            self.response.status = 401
            return
        # If we get here then we know there is a user logged in.
        user_note = GetUserNote(user)
        if user_note is None:
            # No current note, so create one.
            user_note = UserNote(parent=root_parent())
            user_note.user = user
        user_note.note = self.request.get('note')
        user_note.put()  # Save the updated note in datastore
        self.redirect('/update_note')  # Redirect the user to GET /update_note

class AjaxGetCurrentNote(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is None:
            # No user is logged in, so don't return any value.
            self.response.status = 401
            return
        user_note = GetUserNote(user)
        note = ''
        if user_note is not None:
            # If there was a current note, update note.
            note = user_note.note
        # build a dictionary that contains the data that we want to return.
        data = {'note': note}
        # Note the different content type.
        self.response.headers['Content-Type'] = 'application/json'
        # Turn data dict into a json string and write it to the response
        self.response.write(json.dumps(data))


# The app config
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/update_note', UpdateNote),
    ('/ajax/get_current_node', AjaxGetCurrentNote),
], debug=True)
