/**************************
 * Name: SCUTUM GUI
 * Author K4YT3X
 * Date Created: I can't remember
 * Last Modified: Oct 1, 2017
 *
 * For SCUTUM 2.6.0 beta 5
**************************/
#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <iostream>
#include <string>

MainWindow::MainWindow(QWidget *parent):QMainWindow(parent), ui(new Ui::MainWindow){
    ui->setupUi(this);
    int scutumStatus = getScutumStatus();
    if (scutumStatus == 0) {
        QPalette platte;
        platte.setColor(QPalette::WindowText,Qt::green);
        ui->statusLabel->setText("ENABLED");
        ui->statusLabel->setPalette(platte);
    } else {
        QPalette platte;
        platte.setColor(QPalette::WindowText,Qt::red);
        ui->statusLabel->setText("DISABLED");
        ui->statusLabel->setPalette(platte);
    }

}

MainWindow::~MainWindow(){
    delete ui;
}

int MainWindow::getScutumStatus(){
    return system("/lib/systemd/systemd-sysv-install is-enabled scutum");
}

void MainWindow::on_enableButton_clicked()
{
    QPalette platte;
    platte.setColor(QPalette::WindowText,Qt::green);
    ui->statusLabel->setText("ENABLED");
    ui->statusLabel->setPalette(platte);
    system("gksu \"systemctl enable scutum\"");
    system("gksu \"service scutum start\"");
}

void MainWindow::on_disableButton_clicked()
{
    QPalette platte;
    platte.setColor(QPalette::WindowText,Qt::red);
    ui->statusLabel->setText("DISABLED");
    ui->statusLabel->setPalette(platte);
    system("gksu \"systemctl disable scutum\"");
    system("gksu \"service scutum stop\"");
}

void MainWindow::on_disabletempButton_clicked()
{
    QPalette platte;
    platte.setColor(QPalette::WindowText,Qt::red);
    ui->statusLabel->setText("TEMP-DIS");
    ui->statusLabel->setPalette(platte);
    system("gksu \"scutum --reset\"");
}
