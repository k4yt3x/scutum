#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <iostream>
#include <string>
#include <QtCore/QFile>
#include <QtCore/QTextStream>

MainWindow::MainWindow(QWidget *parent):QMainWindow(parent), ui(new Ui::MainWindow){
    ui->setupUi(this);
    int scutumStatus = getScutumStatus();
    if (scutumStatus == 1) {
        QPalette platte;
        platte.setColor(QPalette::WindowText,Qt::red);
        ui->statusLabel->setText("DISABLED");
        ui->statusLabel->setPalette(platte);
    } else if (scutumStatus == 0) {
        QPalette platte;
        platte.setColor(QPalette::WindowText,Qt::green);
        ui->statusLabel->setText("ENABLED");
        ui->statusLabel->setPalette(platte);
    }

}

MainWindow::~MainWindow(){
    delete ui;
}

int MainWindow::getScutumStatus(){
    QFile scutumCFG("/etc/scutum.conf");
    scutumCFG.open(QIODevice::ReadOnly);
    QTextStream cfgstream(&scutumCFG);
    const QString content = cfgstream.readAll();
    scutumCFG.close();
    if (content.contains("enabled=true")) {
            return 0;
    } else {
        return 1;
    }
}

void MainWindow::on_enableButton_clicked()
{
    QPalette platte;
    platte.setColor(QPalette::WindowText,Qt::green);
    ui->statusLabel->setText("ENABLED");
    ui->statusLabel->setPalette(platte);
    system("gksu \"scutum --enable\"");
}

void MainWindow::on_disableButton_clicked()
{
    QPalette platte;
    platte.setColor(QPalette::WindowText,Qt::red);
    ui->statusLabel->setText("DISABLED");
    ui->statusLabel->setPalette(platte);
    system("gksu \"scutum --disable\"");
}

void MainWindow::on_disabletempButton_clicked()
{
    QPalette platte;
    platte.setColor(QPalette::WindowText,Qt::red);
    ui->statusLabel->setText("TEMP-DIS");
    ui->statusLabel->setPalette(platte);
    system("gksu \"scutum --reset\"");
}
