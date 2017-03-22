%% script to make background transparant by creating alpha channel of jpg img and save as png
clear;
% to do: 29 30 34 35 38 40 41 65 107 128 164
files = dir('face*.jpg');
files = {files(:).name};
for cf = 1:numel(files)
    disp(['converting ' pwd filesep files{cf}]);
    image = imread([pwd filesep files{cf}]);
    if size(image,3)>1
        image = rgb2gray(image);
    end
    transval = image(1,1);
    alphamask = ones(size(image));
    alphamask(image>=transval-2 & image<=transval+2) = 0; % how lenient is the algorithm
    L = bwlabel(~alphamask,4);
    labels = unique(L(L>0));
    % only take the backround
    alphamask = ones(size(image));
    for c=1:numel(labels)
        if numel(find(L==labels(c)))>3000 % this indicates the minimum surface to replace
            alphamask(L==labels(c))=0;
        end
    end
    %imshow(alphamask);
    imwrite(image,[pwd filesep files{cf}(1:end-3) 'png'],'png','Alpha',alphamask);
end