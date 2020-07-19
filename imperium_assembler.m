pkg load statistics;
close all;
clear all;
clc;

% --- CONFIGURATION --- %
% Load configuration from .cfg file
originalFolder = pwd();
display("loading configuration file");
configurationFile = "./configuration.cfg";
run(configurationFile)

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
      combined_im(inf_row:sup_row, inf_col:sup_col,:) = im(:,:,:);
      combined_alpha(inf_row:sup_row, inf_col:sup_col,:) = alphaim(:,:,:);
      %combined image in format 0-255
   endfor
endfor

% --- ALPHA CONTRAST AND COMBINATION WITH RGB --- %
display("adjusting alpha");
combined_alpha = floor((combined_alpha./255)+0.1);
triple_alpha = cat(3,combined_alpha,combined_alpha,combined_alpha);
combined_im = combined_im .* triple_alpha;
combined_im(:,:,2) = combined_im(:,:,2) + ((1-combined_alpha).*255);


% --- COLOR SIMPLIFICATION --- %
display("simplifying colors");
[ImIx,ImMap] = rgb2ind(combined_im);
ncenters = min((256-64)-2, size(ImMap,1));
[nearcenter, centers, ~, ~] = kmeans (ImMap, ncenters);

% ImMap is in double
% combined_im is in uint8
ImMap = centers;
%@TODO: replace for 
old_ImIx = ImIx;
for i = [1:size(ImIx,1)]
  for j = [1:size(ImIx,2)]
    ImIx(i,j) = (nearcenter(ImIx(i,j)+1));
  endfor
endfor

% Transform ImMap into a 128 table
tmp_ImMap = ImMap;
ImMap = zeros(256,3);
ImMap((64+2)+1:end,:)=tmp_ImMap;
ImIx = ImIx+64+2;
ImMap(64+1,:) = [0, 1, 0];
ImMap(64+2,:) = [1, 0, 1];
display("setting alpha");
for i = [1:size(ImIx,1)]
  for j = [1:size(ImIx,2)]
    if combined_alpha(i,j) < 0.1
      ImIx(i,j) = 64+1;
    endif
  endfor
endfor


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
ImIx_f = zeros(size(ImIx,1)+n_frames-1, size(ImIx,2)+7)+1;
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
ImIx_f(:,frames_j)=64+2;
ImIx_f(frames_i,:)=64+2;
% --- SAVE IMAGE --- %
%ImIx_f = ImIx_f -1;
imwrite(ImIx_f,ImMap,"resultado.BMP");%,"Alpha",combined_alpha)

cd(originalFolder)
rmpath(strcat(pwd,"/octave_functions"));