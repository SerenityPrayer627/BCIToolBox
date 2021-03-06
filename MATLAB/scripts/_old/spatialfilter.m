% References
%
% Spatial filters for the classification of event-related potentials
% Urich Hoffmann, Jean-Marc Vesin and Touradj Ebrahimi
%

function f = spatialfilter(E,pk)

K = length(E);

if length(pk) ~= K
   fprintf("Error : Dimention of pk is wrong.\n");
   return 
end

T = size(E{K},2);
N = 0;
for k = 1:K
   N = N + size(E{k},3);
end

%% Calculate Sb

fprintf("Calculating Sb : ");

count = 0;
for t = 1:T
    fprintf("#");
    for k = 1:K
        count = count + 1;
        Sb(:,:,count) = pk(k).*((ekt(E,k,t)-et(E,t))*(ekt(E,k,t)-et(E,t))');
    end
end
Sb = sum(Sb,3);
fprintf("\n");

%% Calculate Sw

fprintf("Calculating Sw : ");

count = 0;
for t = 1:T
    fprintf("#");
    for k = 1:K
        for i = 1:size(E{k},3)
            count = count + 1;
            Sw(:,:,count) = (eit(E,i,t,k)-ekt(E,k,t))*(eit(E,i,t,k)-ekt(E,k,t))';
        end
    end
end
Sw = sum(Sw,3)./N;
fprintf("\n");

%% solving a generalized eigenvalue problem

fprintf("Solving a generalized eigenvalue problem.\n");

[vec,lambda] = eig(Sb,Sw);
[~,ind]=sort(diag(lambda),'descend');
vec=vec(:,ind);

f = vec;

end

%% function part

function e = eit(E,i,t,k)
    e = E{k}(:,t,i);
end

function e = et(E,t)
    K = length(E);
    e = [];
    for k = 1:K
       e = cat(3,e,E{k});
    end
    e = mean(e,3);
    e = e(:,t);
end


function e = ekt(E,k,t)
    e = mean(E{k},3);
    e = e(:,t);
end