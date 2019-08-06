# BoondManager-Auto-Holidays-Validation
This repository allows you to validate holidays request from your employees. <br />
It can be used by the human ressources of any company generating its payslip from BoonManager. <br />
This repository contains an executable button, such that any human ressources employee can use it once it is downloaded. <br />
It produces a google drive spreadhsheet with one worksheet per employee with the details of the computations and allows the human ressources to accelerate their process of holiday requests. <br />

Example of output : <br />

![](example_img_output.png)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system. 

### Prerequisites

Install pip <br />
Install python <br />
Install virtualenv <br />


### Installing

1. You first need to create a key and save it in the "client_secret.json" file <br /> 
Very nice explanation to create a secret key from GCP here
https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

2. Import the example_output.xslx file on your google drive and follow the steps of 1., specify the id_sheet in RENSEIGNEZ_MOI.txt by the id of the spreadsheet

3. Get the pdf payslip of the empoloyees and save it as "Paies.pdf" in 

4. Get the csv. file of holidays request from employees "absences_en_attente_de_validation.csv" and the file of holidays acceptances "absences_validées.csv". <br /> 
These files are uploaded from BoonManager (option utf-8, detailed) <br /> (help : https://support.boondmanager.com/hc/fr/articles/205743519-G%C3%A9rer-les-demandes-d-absences)

5. If the name of the files are differents from the one written in 1. 2. 3., configure their names in RENSEIGNEZ_MOI.txt

6. In the LANCER_MOI.command, change the first line by the path of your directory

7. Launch the code with the LANCER_MOI.command button
  

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Florian Bastin** - www.linkedin.com/in/florian-bastin-08940b131 

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
