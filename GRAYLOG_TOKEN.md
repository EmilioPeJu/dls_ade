The token used in dls_last_release.py was created for the user
"dls_ade" with read-only permissions, using the REST API and
following the instructions here:

https://docs.graylog.org/en/2.2/pages/configuration/rest_api.html

Note that at the time of writing, the version of Graylog in use 
at Diamond is not the latest, so the buttons to do these
operations through the web interface are not yet present.

Steps to reproduce:

- Create the user through the web interface

- Give that user admin privileges temporarily (otherwise it
  doesn't seem to be able to make tokens)

- Create a new token through the API: (will prompt for password, this
  is in the controls password DB)

  curl -u <user>> -H 'Accept: application/json' -X POST
  'https://graylog2.diamond.ac.uk/api/users/<user>/tokens/<name for new
   token>?pretty=true'

- Change the user's permissions back to something minimal - it must
  at least be able to do searches but shouldn't be admin. There is a
  role already defined which is suitable.

- Test the token works
