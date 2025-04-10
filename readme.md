# Image describer prototype

Automatic image descriptions service: Describing images from specific events to the blind.

## Background

Many adaptive programs gather images that were taken of people during the course of the program.
For example, paradox Sports participants often take photos of each other.
Blind people in these programs often cannot distinguish photos of each participant and don’t know which photos include them, or are meaningful to save.
Therefore, people will try to label their images with some sort of alt text, or textual description of the image.
Paradox sports, a Boulder based adaptive climbing organization, does this using the description field in Google Drive’s details pane.
Some participants are good at doing this, but the majority of people are too busy/lazy to do this, and thus most images are useless for blind participants, being random blobs of meaninglessness counting against their cloud storage.
This prototype allows taking a large corpus of images, and a context.csv file, and automatically analyzing the images.
Currently, the prototype analyzes all images with the given context against the chosen model.
A context is used to tell the ai, in english for now, what properties an entity such as a person, climbing route, trail, etc. has.
This uses English.
Perhaps, a later version of the app could have someone pick an image and draw the info they want on the image for the AI.
Setting can be specified in config.
A setting describes the general scene so that the AI can contextualize the image as part of an event.
To run this prototype, do the following:

- install:

  ```shell
  pip install -r requirements.txt
  ```

- Get an api key for the ai agent you want, Anthropic, Gemini, or OpenAI.
- create a `.env` file.
- Place your api key in the `.env` file using standard conventions, `ANTHROPIC_AI_API_KEY` etc.
- copy sample_config.ini to config.ini and modify it per its instructions.
- Point to a real folder of images.
- Create a context.csv, and describe entities in your images in enough detail to give the AI an idea of how to identify.

  This is an example context.csv.

```csv
Person,Derek,"A climber wearing all black. When his face is visible, a beanie covers his eyes"
Route,The Rigid Designator,A 120' tall column of vertical blue/gray ice directly next to another 110' pillar of ice. The left pillar is known by multiple names: The Speer; The Gargoyle depending on who you ask.
...
```

The following is a design I made for the system as I currently envision it.

## Overview

With the advent of modern gen-AI systems, it is possible to give a prompt to an AI, telling the AI that it is tasked with explaining an image to a blind person.
The prompt is used to generate data in a specific format for the automated system to parse.
Given that blind people need to know which photos include them, it is desirable for the system to have a method to identify people and objects in the photos and give them a name.
This is not automatable, without the ai being given some sort of human created person description.
The image descriptions can be enhanced by giving the AI system some sort of setting for which the photos were taken.
Generated image descriptions should be put somewhere useful, whether that be a spreadsheet, or embedded into the file, or both.
Note that many of these images, especially climbing related images, are taken from behind the user, thus good facial recognition cannot be relied upon.
Techniques for advanced image recognition, such as providing the AI systems referencne image data of a person, or using traditional image analysis tooling to give the AI coordinates of objects of interest may be explored at a future date.
This system will take a directory of (possibly nested directories of) image files and describe them using context data.
Each image is sent to the AI system, attaching the repository of info that is used to help the AI identify people/objects/scenes to the descriptions.
Then, once the ai system has described each image, the system will attach the description somewhere useful, rename the file to include a short description (if the detector detects that the file doesn’t already have some useful name), and present a subset of the images to the user for judgement.
If the user choses to proceed, The system will attempt to take the list of people, and organize the images into directories for each person/people/object detected.
This will happen using the existing directory structure, since many such outings have people upload images to specific folders with each person’s name attached to maintain attribution of who originally took the photo.
The results will be downloadable, or committed back to the original repository.

## Detailed design

A modular system is desired allowing maximum flexibility for the purposes of image recognition and file storage medium.
For example, the system will eventually be a web based property.
This web based system may have multiple ways of uploading the images, whether that be uploading a zip file of images, giving the system access to local files via a socket and some local code, sharing a Google Drive with the images, etc.
The system should be configurable, so that mock file systems and mock AI generators can be swapped in for maximum testability.
Pydantic is used to validate schemas for context and descriptions.
Additionally, staging and production systems may use different secrets, etc.
A flexible INI based config system is used to capture config options.
This system allows capturing configs for specific modules, I.E. [files] [[google_drive]] or [ai] [[openai]] can store specific options.
Secrets are not stored in this config, but are piped in via environment variables.
A logging system will log errors as they occur.
Python’s async features are extensively used to maximize machine resources for IO bound tasks.
In case something goes wrong, and due to the high cost of using an ai system to get image descriptions, a method for resuming progress after a crash/failure needs to be implemented.
In the prototype, this is achieved with saving the csv line by line as data is added, but some sort of progress capture will be needed, so that upon resuming a failed describe, the images are not re-analyzed.

### AI systems

The system needs to allow for ai systems to be swapped on the fly.
An AI system is abstract, so that the calling code can interact with all systems in the same way.
In this way, identifying people in images could be automated using a different AI system from the alt text gathering, or so that different rendering strategies could be used/tested for maximum alt text quality.
I am currently using pydantic_ai to work with any supported models.
Simply selecting a model uses the correct config and apis. pydantic_ai also has a robust testing framework, both for testing fake model output and for functionally testing any added tools.

### Pydantic powered entity builder

An entity builder system that allows adding entities to a database will be needed.
This will be achieved mostly via javascript/typescript in a vue app.
The backend python implementation will contain a Pydantic model that handles validating the input data.
The python implementation will also allow importing the entities from csv for testing, and allowing me to build out the backend via python, since I am already working from a python based prototype.

### File system abstraction

A filesystem abstraction will be used to allow seamless work with Google Drive, Dropbox, local files, uploaded zip archives, etc.
The filesystem abstraction layer will be based on fsspec.
To start with, zip files, and for the cli app, local filesystems will be supported.
I will need to implement the oauth flows for Googe Drive and Dropbox, etc. later.
This abstract file system layer will allow the code to seamlessly work across different user-provided file system types withoutu having to add boilerplate to get the images into a common format.

### User interface

A frontend browser user interface will be created using Vue.
This product will be a workflow based on a simple wizard.

- A method for getting a repository of files into the app.
- A context builder interface.
- A processing screen
- A viewing interface to see some examples of the processed images.
- A commit interface to get the processed images back into the original file repository.

#### File uploaders

The file uploader step will include multiple methods to get your files into the app.
To start with, a simple zip upload option will exist.
The file uploader will be a list of file upload methods.
Each method links off to a workflow for uploading files.
Some of these methods will need to implement an Oauth flow.
The MVP will only implement a zip uploader.

#### Context builder

The context builder page will include a text field for adding the setting, with text explaining what a setting is.
The app will suggest that people describe, in 200 words or less, the context for the batch of images.
For example, “A birthday party in an outdoor setting in California.” “A bird watching day in a park in Wyoming.” or “An adaptive climbing weekend in Joshua tree national park.” It may be desirable to add a fast follow for including ai assistance, similar to prompt creation tools, that help a user generate the best setting for the ai.
The page will also include a table of entities.
The columns will be category, name, description, and actions.
Below the table, and add row button will exist, to add a row to the table.
The final row of the table will be in edit mode, and categories can be added in a combobox like widget where categories are suggested from a small preexisting list, or from other already used categories.
Any row can be turned into an editable row by clicking edit.
The edit button will turn into a done button for each row once complete.
At the bottom of the screen, a start processing button will be present.
This will bring up the privacy alert splash screen.

#### Processing screen:

A processing screen will show the number of images that have been processed.
I have not yet figured out if the app will pole, or if there can be some sort of dynamic socket interface.
I also may show the last processed image at random, so that each processed image is presented for 30 or so seconds with its description and recognized entities+confidences.

#### Viewing interface

A selection of images will be sampled in the view interface.
The identified entities and short description’s file name will be shown along side the image, along with the long description.
There may be a way to do a 1shot re-analyze for that image with clearer context on who is present.
A “show next” button will show the next image.
Cancel and commit buttons will exist, to cancel or start the commit for the batch process.

#### Commit interface.

To start with for the MVP, a zip file will be downloadable.
Committing back to network file providers will eventually be added.
This will not be supported for the MVP.

## Privacy considerations

Some participants in various events do not want to have their likeness identified by AI systems.
Given that this process cannot be achieved without AI, a simple privacy screen will tell people that they should ensure people are okay with participants in the images being used for ai, and start over after images of those people have been removed.

## Internationalization

It will be necessary to internationalize the UI for this system.
Unfortunately, I do not know if Claud, openAI and gemini will generate decent ai descriptions in non-english locales.
The ui will follow best practices for i18n so this can be achieved.

## Accessibility

WCAG best practices will be followed in designing the app, to ensure it is at least WCAG 2.2 AA.
AAA will be the target for the app once all providers are implemented.

Roadmap:
1 story point is approx 1 ideal day of work for a senior dev competent in the given task.
Backend:
General prototype: took about 2
Refactor to add pydantic models: .5
Add filespec support for local files: .5
Refactor to give the ai entity descriptions: 1
Unit Test prototype and refactors: 1
Integration test workflow: 2
Scaffolding and refactor for web server: 3
Add entities endpoint to a web server: 1
Add file upload to server: 1
Add failure resume: 1 (not needed for mvp)
Implement processing endpoint: 2
Implement commit endpoint: 1
Oauth for gdrive: 3
MVP points: 13
With gdrive and resume: 17
Frontend:
Basic setup: 1
Zip file Upload workflow: 1
Context builder: 2
Privacy splash: .5
Processing screen: 1
Viewing screen: 2
Commit screen: 1
Polish: 3
Total: 11.5
Total mvp: 24.5
Unexpected time: 12
Expected: 36
