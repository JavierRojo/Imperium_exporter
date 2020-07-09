close all;
clear all;
clc;

% --- CONFIGURATION --- %
% Load configuration from .cfg file
originalFolder = pwd();
configurationFile = "./configuration.cfg";
run(configurationFile)

% n_frames
% resolution_sprite
% input_folder
% output_folder

if size(input_folder,1) == 0
  [colnames, input_folder, ~] = uigetfile ("MultiSelect", "ON");
  cd(input_folder)
  colnames = reshape(colnames,size(colnames,2),size(colnames,1));
else
  cd(input_folder);
  colnames = glob("*[0-9]_[0-9]*.png");
endif
cd(originalFolder)
addpath(strcat(pwd,"/octave_functions"));

% --- COMBINE PNG TEXTURES --- %
combined_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,3,"uint8");
combined_alpha = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
for i = 1:10 %for every frame
  for j = 1:8 %for every direction
      file = name_from_cell(strcat(int2str(j),"_",int2str(i),"\.png"),colnames);
      [im, ~, alphaim] = imread(strcat(input_folder,file));
      inf_row = ((i-1)*resolution_sprite)+1;
      sup_row = i*resolution_sprite;
      inf_col = ((j-1)*resolution_sprite)+1;
      sup_col = j*resolution_sprite;
      combined_im(inf_row:sup_row, inf_col:sup_col,:) = im(:,:,:);
      combined_alpha(inf_row:sup_row, inf_col:sup_col,:) = alphaim(:,:,:);
      %combined image in format 0-255
   endfor
endfor

imwrite(combined_im,"resultado.png","Alpha",combined_alpha)

cd(originalFolder)
rmpath(strcat(pwd,"/octave_functions"));