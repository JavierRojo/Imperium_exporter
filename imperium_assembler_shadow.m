pkg load statistics;
close all;
clear all;
clc;

% --- CONFIGURATION --- %
% Load configuration from .cfg file
originalFolder = pwd();
display("loading configuration file");
configurationFile = "./configuration.cfg";
run(configurationFile);
input_folder = strcat(input_folder,"shadow/");

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
display("combining png images");
combined_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,3,"uint8");
combined_alpha = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
for i = 1:n_frames %for every frame
  for j = 1:8 %for every direction
      file = name_from_cell(strcat(int2str(j),"_",int2str(i),"\.png"),colnames);
      [im, ~, alphaim] = imread(strcat(input_folder,file));
      inf_row = ((i-1)*resolution_sprite)+1;
      sup_row = i*resolution_sprite;
      inf_col = ((j-1)*resolution_sprite)+1;
      sup_col = j*resolution_sprite;
      %combined_im(inf_row:sup_row, inf_col:sup_col,:) = im(:,:,:);
      combined_alpha(inf_row:sup_row, inf_col:sup_col,:) = alphaim(:,:,:);
      %combined image in format 0-255
   endfor
endfor

% --- ALPHA CONTRAST AND COMBINATION WITH RGB --- %
display("adjusting alpha");
combined_alpha = round((combined_alpha./255)+0.1);
%combined_alpha = combined_alpha .* 255;
%imwrite(combined_alpha,"combined_alpha.png");

% --- COLOR SIMPLIFICATION --- %
display("Creating color table");
ImMap = zeros(256,3);
ImMap (1:2,:) = [
0,1,0;
0,0,0;
];
ImIx = combined_alpha;

% --- FRAMES --- %
% 
% ooo|ooo|ooo
% ooo|ooo|ooo
% ooo|ooo|ooo
% ---*---*---
% ooo|ooo|ooo
% ooo|ooo|ooo
% ooo|ooo|ooo
% ---*---*---
% ooo|ooo|ooo
% ooo|ooo|ooo
% ooo|ooo|ooo
% 
disp("adding frames");
ImIx_f = zeros(size(ImIx,1)+n_frames-1, size(ImIx,2)+7);
for i=1:n_frames
  for j=1:8
    if i==1
      if j == 1
        ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite, (j-1)*resolution_sprite+j:(j)*resolution_sprite) = ...
        ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
      else
        ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite+i-1, (j-1)*resolution_sprite+j:(j)*resolution_sprite+j-1) = ...
        ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
      endif
    else
      if j == 1
        ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite+i-1, (j-1)*resolution_sprite+j:(j)*resolution_sprite) = ...
        ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
      else
        ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite+i-1, (j-1)*resolution_sprite+j:(j)*resolution_sprite+j-1) = ...
        ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
      endif
    endif
  endfor
endfor


frames_i = resolution_sprite+1:resolution_sprite+1:n_frames*resolution_sprite+n_frames-1;
frames_j = resolution_sprite+1:resolution_sprite+1:7*resolution_sprite+7;
ImIx_f(:,frames_j)=1;
ImIx_f(frames_i,:)=1;
% --- SAVE IMAGE --- %
ImIx_f = ImIx_f + 1;
imwrite(ImIx_f,ImMap,"resultado_shadow.BMP");%,"Alpha",combined_alpha)

cd(originalFolder)
rmpath(strcat(pwd,"/octave_functions"));