load('output_dir/demo_output_data/mu_vals.mat')
colours = ['b','g','y','r']

for i = 1:size(mu_x,2)
    scatter(mu_x(:,i),mu_y(:,i),colours(i)); axis([0 35 0 30]);
    input("Press any key to continue ...");
end

 
