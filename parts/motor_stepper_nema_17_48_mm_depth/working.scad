// Generated from persisted three_d_model_details. Dimensions in millimetres.
// Nominal layout assembly, not manufacturing geometry.
$fn = 96;
// rear_end_cap
color([0.72, 0.74, 0.76]) translate([0, 0, 0]) rotate([0, 0, 0]) linear_extrude(height=8.0) polygon([[-18.0, -21.0], [18.0, -21.0], [21.0, -18.0], [21.0, 18.0], [18.0, 21.0], [-18.0, 21.0], [-21.0, 18.0], [-21.0, -18.0]]);
// stator_stack
color([0.12, 0.13, 0.15]) translate([0, 0, 8.0]) rotate([0, 0, 0]) linear_extrude(height=32.0) polygon([[-18.0, -21.0], [18.0, -21.0], [21.0, -18.0], [21.0, 18.0], [18.0, 21.0], [-18.0, 21.0], [-21.0, 18.0], [-21.0, -18.0]]);
// front_end_cap
color([0.72, 0.74, 0.76]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([0, 0, 40.0]) rotate([0, 0, 0]) linear_extrude(height=8.0) polygon([[-18.0, -21.0], [18.0, -21.0], [21.0, -18.0], [21.0, 18.0], [18.0, 21.0], [-18.0, 21.0], [-21.0, 18.0], [-21.0, -18.0]]);
translate([-15.5, -15.5, 43.5]) rotate([0, 0, 0]) cylinder(d=3.0, h=4.52);
translate([-15.5, 15.5, 43.5]) rotate([0, 0, 0]) cylinder(d=3.0, h=4.52);
translate([15.5, -15.5, 43.5]) rotate([0, 0, 0]) cylinder(d=3.0, h=4.52);
translate([15.5, 15.5, 43.5]) rotate([0, 0, 0]) cylinder(d=3.0, h=4.52);
}
// pilot
color([0.72, 0.74, 0.76]) translate([0, 0, 48]) rotate([0, 0, 0]) cylinder(d=22.0, h=2.0);
// output_d_shaft
color([0.62, 0.65, 0.69]) translate([0, 0, 48]) rotate([0, 0, 0]) difference() {
translate([0, 0, 0]) rotate([0, 0, 0]) cylinder(d=5.0, h=24.0);
translate([0, 4.5, 8.99]) rotate([0, 0, 0]) translate([-5.0, -2.5, 0]) cube([10.0, 5.0, 15.02]);
}
// rear_screw_-15.5_-15.5
color([0.62, 0.65, 0.69]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([-15.5, -15.5, 0]) rotate([0, 0, 0]) cylinder(d=4.4, h=0.7);
translate([-15.5, -15.5, -0.01]) rotate([0, 0, 0]) translate([-1.5, -0.35, 0]) cube([3, 0.7, 0.4]);
translate([-15.5, -15.5, -0.01]) rotate([0, 0, 0]) translate([-0.35, -1.5, 0]) cube([0.7, 3, 0.4]);
}
// rear_screw_-15.5_15.5
color([0.62, 0.65, 0.69]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([-15.5, 15.5, 0]) rotate([0, 0, 0]) cylinder(d=4.4, h=0.7);
translate([-15.5, 15.5, -0.01]) rotate([0, 0, 0]) translate([-1.5, -0.35, 0]) cube([3, 0.7, 0.4]);
translate([-15.5, 15.5, -0.01]) rotate([0, 0, 0]) translate([-0.35, -1.5, 0]) cube([0.7, 3, 0.4]);
}
// rear_screw_15.5_-15.5
color([0.62, 0.65, 0.69]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([15.5, -15.5, 0]) rotate([0, 0, 0]) cylinder(d=4.4, h=0.7);
translate([15.5, -15.5, -0.01]) rotate([0, 0, 0]) translate([-1.5, -0.35, 0]) cube([3, 0.7, 0.4]);
translate([15.5, -15.5, -0.01]) rotate([0, 0, 0]) translate([-0.35, -1.5, 0]) cube([0.7, 3, 0.4]);
}
// rear_screw_15.5_15.5
color([0.62, 0.65, 0.69]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([15.5, 15.5, 0]) rotate([0, 0, 0]) cylinder(d=4.4, h=0.7);
translate([15.5, 15.5, -0.01]) rotate([0, 0, 0]) translate([-1.5, -0.35, 0]) cube([3, 0.7, 0.4]);
translate([15.5, 15.5, -0.01]) rotate([0, 0, 0]) translate([-0.35, -1.5, 0]) cube([0.7, 3, 0.4]);
}
// connector
color([0.065, 0.075, 0.09]) translate([0, 21.0, 2]) rotate([0, 0, 0]) translate([-7.0, -1.5, 0]) cube([14, 3, 5]);
