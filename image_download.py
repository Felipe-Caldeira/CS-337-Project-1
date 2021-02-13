from simple_image_download import simple_image_download as simp

response = simp.simple_image_download
  
def downloadImages(year, person, award):
    response().download("Golden Globes " + str(year) + " " + person + " " + award, 5) 