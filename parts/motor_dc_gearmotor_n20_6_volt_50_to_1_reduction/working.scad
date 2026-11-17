// Generated from persisted three_d_model_details. Dimensions in millimetres.
// Nominal layout assembly, not manufacturing geometry.
$fn = 96;
// rear_cap
color([0.065, 0.075, 0.09]) translate([0, 0, 0]) rotate([0, 0, 0]) intersection() {
translate([0, 0, 0]) rotate([0, 0, 0]) cylinder(d=12.0, h=2.0);
translate([0, 0, 0]) rotate([0, 0, 0]) translate([-6.0, -5.0, 0]) cube([12.0, 10.0, 2.0]);
}
// motor_can
color([0.62, 0.65, 0.69]) translate([0, 0, 0]) rotate([0, 0, 0]) intersection() {
translate([0, 0, 2.0]) rotate([0, 0, 0]) cylinder(d=12.0, h=15.0);
translate([0, 0, 2.0]) rotate([0, 0, 0]) translate([-6.0, -5.0, 0]) cube([12.0, 10.0, 15.0]);
}
// gearbox_plate_0
color([0.67, 0.48, 0.2]) translate([0, 0, 17.0]) rotate([0, 0, 0]) translate([-6.0, -5.0, 0]) cube([12.0, 10.0, 1.0]);
// gearbox_plate_1
color([0.67, 0.48, 0.2]) translate([0, 0, 0]) rotate([0, 0, 0]) difference() {
translate([0, 0, 25.0]) rotate([0, 0, 0]) translate([-6.0, -5.0, 0]) cube([12.0, 10.0, 1.0]);
translate([-4.5, 0, 24.99]) rotate([0, 0, 0]) cylinder(d=1.6, h=1.02);
translate([4.5, 0, 24.99]) rotate([0, 0, 0]) cylinder(d=1.6, h=1.02);
}
// gearbox_pillar_-4.6_-3.6
color([0.67, 0.48, 0.2]) translate([-4.6, -3.6, 18.0]) rotate([0, 0, 0]) cylinder(d=1.3, h=7.0);
// gearbox_pillar_-4.6_3.6
color([0.67, 0.48, 0.2]) translate([-4.6, 3.6, 18.0]) rotate([0, 0, 0]) cylinder(d=1.3, h=7.0);
// gearbox_pillar_4.6_-3.6
color([0.67, 0.48, 0.2]) translate([4.6, -3.6, 18.0]) rotate([0, 0, 0]) cylinder(d=1.3, h=7.0);
// gearbox_pillar_4.6_3.6
color([0.67, 0.48, 0.2]) translate([4.6, 3.6, 18.0]) rotate([0, 0, 0]) cylinder(d=1.3, h=7.0);
// illustrative_gear_disc_0
color([0.67, 0.48, 0.2]) translate([1.8, 0, 18.0]) rotate([0, 0, 0]) cylinder(d=6.4, h=1.4);
// illustrative_gear_disc_1
color([0.67, 0.48, 0.2]) translate([-1.8, 0, 20.0]) rotate([0, 0, 0]) cylinder(d=6.4, h=1.4);
// illustrative_gear_disc_2
color([0.67, 0.48, 0.2]) translate([1.8, 0, 22.0]) rotate([0, 0, 0]) cylinder(d=6.4, h=1.4);
// output_d_shaft
color([0.62, 0.65, 0.69]) translate([0, 0, 26.0]) rotate([0, 0, 0]) difference() {
translate([0, 0, 0]) rotate([0, 0, 0]) cylinder(d=3.0, h=9.0);
translate([0, 2.5, 0.99]) rotate([0, 0, 0]) translate([-3.0, -1.5, 0]) cube([6.0, 3.0, 8.02]);
}
// terminal_-3
color([0.67, 0.48, 0.2]) translate([-3, 0, -2.5]) rotate([0, 0, 0]) translate([-0.75, -0.2, 0]) cube([1.5, 0.4, 2.5]);
// terminal_3
color([0.67, 0.48, 0.2]) translate([3, 0, -2.5]) rotate([0, 0, 0]) translate([-0.75, -0.2, 0]) cube([1.5, 0.4, 2.5]);
