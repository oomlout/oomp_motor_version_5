// Generated from persisted three_d_model_details. Dimensions in millimetres.
// Nominal layout assembly, not manufacturing geometry.
$fn = 96;
// housing_half_0
color([0.075, 0.34, 0.68]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([0, 0, 0]) rotate([0, 0, 0]) linear_extrude(height=10.23) polygon([[-34.75, -7.0], [-30.75, -11.0], [-0.75, -11.0], [3.25, -7.0], [3.25, 7.0], [-0.75, 11.0], [-30.75, 11.0], [-34.75, 7.0]]);
translate([-3.75, -8.75, -0.1]) rotate([0, 0, 0]) cylinder(d=3.0, h=20.9);
translate([-3.75, 8.75, -0.1]) rotate([0, 0, 0]) cylinder(d=3.0, h=20.9);
}
// housing_half_1
color([0.075, 0.34, 0.68]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([0, 0, 10.469999999999999]) rotate([0, 0, 0]) linear_extrude(height=10.23) polygon([[-34.75, -7.0], [-30.75, -11.0], [-0.75, -11.0], [3.25, -7.0], [3.25, 7.0], [-0.75, 11.0], [-30.75, 11.0], [-34.75, 7.0]]);
translate([-3.75, -8.75, -0.1]) rotate([0, 0, 0]) cylinder(d=3.0, h=20.9);
translate([-3.75, 8.75, -0.1]) rotate([0, 0, 0]) cylinder(d=3.0, h=20.9);
}
// motor_can
color([0.62, 0.65, 0.69]) translate([3.25, 0, 10.35]) rotate([0, 90, 0]) cylinder(d=18.0, h=28.5);
// motor_end_cap
color([0.065, 0.075, 0.09]) translate([31.75, 0, 10.35]) rotate([0, 90, 0]) cylinder(d=18.0, h=3);
// output_shaft
color([0.86, 0.85, 0.81]) translate([-23.0, 0, 20.7]) rotate([0, 0, 0]) difference() {
translate([0, 0, 0]) rotate([0, 0, 0]) cylinder(d=5.4, h=9.0);
translate([0, -4.5, -0.01]) rotate([0, 0, 0]) translate([-5.4, -2.7, 0]) cube([10.8, 5.4, 9.02]);
translate([0, 4.5, -0.01]) rotate([0, 0, 0]) translate([-5.4, -2.7, 0]) cube([10.8, 5.4, 9.02]);
}
// terminal_-4
color([0.67, 0.48, 0.2]) translate([35.75, -4, 10.35]) rotate([0, 0, 0]) translate([-1.0, -1.0, 0]) cube([2, 2, 0.5]);
// terminal_4
color([0.67, 0.48, 0.2]) translate([35.75, 4, 10.35]) rotate([0, 0, 0]) translate([-1.0, -1.0, 0]) cube([2, 2, 0.5]);
