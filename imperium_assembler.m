pkg load statistics;
close all;
clear all;
clc;
MIN_LVL_COLOR = 72;

% --- CONFIGURATION --- %
% Load configuration from .cfg file
originalFolder = pwd();
display("loading configuration file");
configurationFile = "./configuration.cfg";
run(configurationFile);
input_folder_color = strcat(input_folder,"color/");
input_folder_level = strcat(input_folder,"level/");
input_folder_player = strcat(input_folder,"player/");

if size(input_folder_color,1) == 0
  [colnames, input_folder_color, ~] = uigetfile ("MultiSelect", "ON");
  cd(input_folder_color)
  colnames = reshape(colnames,size(colnames,2),size(colnames,1));
else
  cd(input_folder_color);
  colnames_color = glob("*[0-9]_[0-9]*.png");
  cd(originalFolder)
  cd(input_folder_level);
  colnames_level = glob("*[0-9]_[0-9]*.png");
  cd(originalFolder)
  cd(input_folder_player);
  colnames_player = glob("*[0-9]_[0-9]*.png");
endif
cd(originalFolder)
addpath(strcat(pwd,"/octave_functions"));

% --- COMBINE PNG TEXTURES --- %
display("combining png images");
[combined_level_im, combined_player_im, combined_im, combined_alpha] =...
combine_img(colnames_color, input_folder_color, input_folder_level, input_folder_player, n_frames, resolution_sprite);
  
% --- ALPHA CONTRAST AND COMBINATION WITH RGB --- %
display("adjusting alpha");
combined_alpha = floor((combined_alpha./255)+0);
combined_level_im = floor((combined_level_im./255)+0);
combined_player_im = floor((combined_player_im./255)+0);
triple_level_combined = cat(3,combined_level_im,combined_level_im,combined_level_im);
triple_player_combined = cat(3,combined_player_im,combined_player_im,combined_player_im);
triple_alpha = cat(3,combined_alpha,combined_alpha,combined_alpha);
combined_im = combined_im .* triple_alpha;
combined_im(:,:,2) = combined_im(:,:,2) + ((1-combined_alpha).*255);


% --- COLOR SIMPLIFICATION --- %
display("simplifying colors");
%Delete colors that won't be used (LEVEL)
level_saturation = combined_im .* triple_level_combined;
combined_im = combined_im .* (1-triple_level_combined);
combined_im(:,:,2) = combined_im(:,:,2) + combined_level_im.*255;

%Delete colors that won't be used (PLAYER)
player_saturation = combined_im .* triple_player_combined;
combined_im = combined_im .* (1-triple_player_combined);
combined_im(:,:,2) = combined_im(:,:,2) + combined_player_im.*255;

%Simplify all the other colors
[ImIx,ImMap] = rgb2ind(combined_im);
ncenters = min((256-64)-2-n_level_colors, size(ImMap,1));
[nearcenter, centers, ~, ~] = kmeans (ImMap, ncenters);

% ImIx marca los índices a la lista grande original de colores de la imagen.
ImMap = centers;
ImIx = nearcenter(ImIx+1);

% --- COLOR SIMPLIFICATION LEVEL COLOR--- %
display("simplifying colors of level color texture");
[ImIx_lvl, ImMap_lvl] = simplify_level_color(level_saturation, n_level_colors);
ImMap_lvl = map_lvl_color(MIN_LVL_COLOR, ImMap_lvl);

% --- COLOR SIMPLIFICATION PLAYER COLOR--- %
display("simplifying colors of player color texture");
hsv_player = rgb2hsv (player_saturation);
% Colors in table (0-63) don't matter, only the index in the image
hsv_modified = map_player_color(hsv_player);
sat =  hsv_modified(:,:,2); 
val = hsv_modified(:,:,3);
% 0.9999 prevents the saturation=1 case
ImIx_ply = floor(val *0.99999 * 8)*8 + floor(sat*0.99999*8);

% --- COMBINATION OF LEVEL AND COLOR AND PLAYER --- %
[ImIx,ImMap] = combine_results(ImMap, ImMap_lvl, ImIx_ply, ImIx_lvl, ImIx, combined_level_im, combined_player_im, combined_alpha, n_level_colors);

% --- FRAMES --- % 
disp("adding frames");
ImIx_f = add_frames(ImIx, n_frames,resolution_sprite);

% --- SAVE IMAGE --- %
cd(originalFolder)
cd(output_folder)
imwrite(ImIx_f,ImMap,"resultado_final.BMP");%,"Alpha",combined_alpha)
cd(originalFolder)
rmpath(strcat(pwd,"/octave_functions"));