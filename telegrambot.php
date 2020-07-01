<?php
#Take GET-Parameter id, download corrosponding PNG from Twitch and convert it to WEBP. 
header('Content-Type: image/webp');

$png = imagecreatefrompng('https://static-cdn.jtvnw.net/emoticons/v1/' . $_GET["id"] . '/3.0');
imagealphablending($png, true);
imagesavealpha($png, true);
imagepalettetotruecolor($png);

#This will "print" the result to the website.
imagewebp($png, NULL, 100);

imagedestroy($png);
?>

