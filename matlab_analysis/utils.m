classdef utils
    
    methods(Static)

    function dydx = derivative(x, y)
        n = length(y);
        dydx = zeros(1, n);
        dydx(1) = (y(2) - y(1))/(x(2) - x(1));
        for i = 2:length(y)-1
            dydx(i) = (y(i+1) - y(i-1))/(x(i+1) - x(i-1));
        end
        dydx(n) = (y(n) - y(n-1))/(x(n) - x(n-1));
    end
    
    function folderNames = getAllSubFolders(directory)
        startPath = [directory, '/Data'];

        subFolders = genpath(startPath);
        remain = subFolders;
        folderNames = {};
        while true
            [subFolder, remain] = strtok(remain, ':');
            if isempty(subFolder)
                break
            end
            folderNames = [folderNames, subFolder];
        end
    end

    function [episodeFiles, episodeFolders] = getEpisodeFolders(folderNames)
        episodeFiles = {};
        episodeFolders = {};
        for k = 1:length(folderNames)
            folderName = folderNames{k};
            episodeNames = dir(sprintf('%s/Episode_*', folderName));

            if ~isempty(episodeNames)
                fprintf('Processing folder %s\n', folderName);
                for n = 1:length(episodeNames)       
                    episodeFiles = [strcat(episodeNames(n).folder, '/', episodeNames(n).name); episodeFiles];
                    episodeFolders = [episodeNames(n).folder; episodeFolders];
                end
                clc
            end
        end
    end

    function occlusionCoordinatesFolders = getOcclusionCoordinatesFolders(folderNames)
        occlusionCoordinatesFolders = {};
        for k = 1:length(folderNames)
            folderName = folderNames{k};    
            occlusionNames = dir(sprintf('%s/OcclusionCoordinates*', folderName));

            if ~isempty(occlusionNames)
                fprintf('Processing folder %s\n', folderName);
                for n = 1:length(occlusionNames)
                    occlusionCoordinatesFolders = [strcat(occlusionNames(n).folder, '/', occlusionNames(n).name); occlusionCoordinatesFolders];
                end
                clc
            end
        end
    
    end

    function aStarCoordinatesFolders = getAStarCoordinatesFolders(folderNames)
        aStarCoordinatesFolders = {};
        for k = 1:length(folderNames)
            folderName = folderNames{k};    
            aStarNames = dir(sprintf('%s/AStar*', folderName));

            if ~isempty(aStarNames)
                fprintf('Processing folder %s\n', folderName);
                for n = 1:length(aStarNames)
                    aStarCoordinatesFolders = [strcat(aStarNames(n).folder, '/', aStarNames(n).name); aStarCoordinatesFolders];
                end
                clc
            end
        end
    end
    
    end
end