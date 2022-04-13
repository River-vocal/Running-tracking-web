# Running-tracking-web
Django-based web service supporting daily exercising tracking

# Jogger Logger

## Backlog:

### Event model
* Main database model for runs
* Contains fields for title, description, milage, duration, and date.

### Calendar overview
* Calendar style view displaying a month with each day containing titles of events in that day.
* Clicking an empty spot in a day pulls up modal form to submit a new event for that day
* Ajax form submission and reloading for seemless page updating.
* Each user's calendar is visible from their user URL and publicly accessable if logged in

### Statistics overview
* Computed statistics of a user
* Visible to other users
* Average weekly milage, total milage, average pase, etc.

### Team functionality
* Coach superuser can edit calendars of athletes
* Invitations to teams through email or in-app form
* Team calculated statistics

### Register
* The website is availalbe to the general public 
* Each user will register with their name, email, password, role (student/coach/enthusiast)
* OAuth can be used with a google account
* A confirmation is sent to the user upon registering

### Login
* Log in using Google OAuth or extracting login information from organic database

### Set Profile
* Logged in users will be able to set up their profile pages including accepting the team invitations
* Some of the profile information could be long term goals, goals for each week, events attended and the outcome of those events

### User authentication:
* User login screen implemented with registration, etc.
* Redirect all unauthenticated users to login screen.

### Event models:
* Database model to keep track of an event/run.
* Should contain event title, decription, date, duration and distance.

### Non calendar display:
* Display a user's runs in a list format
* Form to submit new run event

### Statistics display
* Seperate page off user URL to display calculated statistics of user run events.

## API used:
* FullCalendar.io
* https://developers.google.com/maps/documentation/javascript/overview
* https://docs.djangoproject.com/en/3.2/
