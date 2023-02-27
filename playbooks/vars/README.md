Use folder for storing variables. If you create variable files with credentials or other sensitive information, then check the gitignore file to ensure that git does not upload them. 

For example. Naming the file credentials.yml will ensure th file is not read by git. 

You can also create separate environments with different specs for each. ie. one for prod, one for dev, etc. To follow the ignore method, first create a folder under vars called env/ and in that
folder add all the environment files like so:

- ./vars/env/prod.yml
- ./vars/env/dev.yml


--happy automating
