//function prueba(l0, l1, l2, l3, l4, l5, checkbox, max_abs, source, slider1, slider2, slider3, slider4, y, frec_start) {
var data = source.data;
var len;
var i;
var mark1 = Boolean(false);
var mark2 = Boolean(false);
var mark3 = Boolean(false);
var mark4 = Boolean(false);
var step = slider1.step;
var x_new;
var y_new;
var delta_x;
var delta_y;
var idx;
l2.visible = false;
l3.visible = false;
l4.visible = false;
l5.visible = false;

// elimino solo el marcador 1
do {
    //l2.visible = false;
    idx = data['x_data'].indexOf("Marcador 1");
    if (idx >= 0) {
        data['x_data'].splice(idx, 1);
        data['y_data'].splice(idx, 1);
    }
}
while (idx >= 0);

// elimino solo el marcador 2
do {
    //l3.visible = false;
    idx = data['x_data'].indexOf("Marcador 2");
    if (idx >= 0) {
        data['x_data'].splice(idx, 1);
        data['y_data'].splice(idx, 1);
        data['x_data'].splice(idx, 1);
        data['y_data'].splice(idx, 1);
    }
}
while (idx >= 0);

// elimino solo el marcador 3
do {
    //l4.visible = false;
    idx = data['x_data'].indexOf("Marcador 3");
    if (idx >= 0) {
        data['x_data'].splice(idx, 1);
        data['y_data'].splice(idx, 1);
    }
}
while (idx >= 0);

// elimino solo el marcador 4
do {
    //l5.visible = false;
    idx = data['x_data'].indexOf("Marcador 4");
    if (idx >= 0) {
        data['x_data'].splice(idx, 1);
        data['y_data'].splice(idx, 1);
    }
}
while (idx >= 0);

checkbox.active.forEach(function (element) {
    // EN CASO DE ACTIVARSE EL CHECK BOX
    switch (element) {
        case 0: // mark 1
            mark1 = true;
            break;
        case 1: // mark 2
            mark2 = true;
            break;
        case 2: // mark 3
            mark3 = true;
            break;
        case 3: // mark 
            mark4 = true;
            break;
        default:
            break;
    }
}
);
if (mark1) {
    l2.visible = true;
    x_new = slider1.value - frec_start;
    y_new = y[Math.round(x_new / step)];
    data['x_data'].push("Marcador 1");
    data['y_data'].push(y_new.toFixed(2).toString() + "dBm @ " + (x_new + frec_start).toFixed(2).toString() + " Hz");
}

if (mark2) {
    l3.visible = true;
    x_new = slider2.value - frec_start;
    y_new = y[Math.round(x_new / step)];
    data['x_data'].push("Marcador 2");
    data['y_data'].push(y_new.toFixed(2).toString() + "dBm @ " + (x_new + frec_start).toFixed(2).toString() + " Hz");
    // aca se calcula por las dudas los delta entre 1 y 2
    if (l2.visible == true) {
        x2 = slider2.value - frec_start;
        x1 = slider1.value - frec_start;
        
        delta_x = Math.abs(slider2.value - slider1.value);
        delta_y = Math.abs(y[Math.round(x2 / step)] - y[Math.round(x1 / step)]);
        data['x_data'].push("Delta 1 a 2");
        data['y_data'].push(delta_x.toFixed(2).toString() + "dBm @ " + delta_y.toFixed(2).toString() + " Hz");
    }
}

if (mark3) {
    l4.visible = true;
    x_new = slider3.value - frec_start;
    y_new = y[Math.round(x_new / step)];
    data['x_data'].push("Marcador 3");
    data['y_data'].push(y_new.toFixed(2).toString() + "dBm @ " + (x_new + frec_start).toFixed(2).toString() + " Hz");
}

if (mark4) {
    l5.visible = true;
    x_new = slider4.value - frec_start;
    y_new = y[Math.round(x_new / step)];
    data['x_data'].push("Marcador 4");
    data['y_data'].push(y_new.toFixed(2).toString() + "dBm @ " + (x_new + frec_start).toFixed(2).toString() + " Hz");
}
source.change.emit();
//}