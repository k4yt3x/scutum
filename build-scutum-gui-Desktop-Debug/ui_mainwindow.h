/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 4.8.7
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QMainWindow>
#include <QtGui/QMenu>
#include <QtGui/QMenuBar>
#include <QtGui/QPushButton>
#include <QtGui/QStatusBar>
#include <QtGui/QToolBar>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralWidget;
    QPushButton *enableButton;
    QPushButton *disableButton;
    QPushButton *disabletempButton;
    QLabel *titleLabel;
    QLabel *statusLabelStatic;
    QLabel *statusLabel;
    QMenuBar *menuBar;
    QMenu *menuMain_C2;
    QMenu *menuHelp;
    QToolBar *mainToolBar;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(600, 282);
        QIcon icon;
        icon.addFile(QString::fromUtf8("../../Python/SCUTUM/scutum-gui.png"), QSize(), QIcon::Normal, QIcon::Off);
        MainWindow->setWindowIcon(icon);
        centralWidget = new QWidget(MainWindow);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        enableButton = new QPushButton(centralWidget);
        enableButton->setObjectName(QString::fromUtf8("enableButton"));
        enableButton->setGeometry(QRect(30, 30, 181, 41));
        disableButton = new QPushButton(centralWidget);
        disableButton->setObjectName(QString::fromUtf8("disableButton"));
        disableButton->setGeometry(QRect(30, 100, 181, 41));
        disabletempButton = new QPushButton(centralWidget);
        disabletempButton->setObjectName(QString::fromUtf8("disabletempButton"));
        disabletempButton->setGeometry(QRect(30, 170, 181, 41));
        titleLabel = new QLabel(centralWidget);
        titleLabel->setObjectName(QString::fromUtf8("titleLabel"));
        titleLabel->setGeometry(QRect(220, 30, 371, 51));
        QFont font;
        font.setPointSize(14);
        titleLabel->setFont(font);
        titleLabel->setTextFormat(Qt::PlainText);
        titleLabel->setAlignment(Qt::AlignCenter);
        statusLabelStatic = new QLabel(centralWidget);
        statusLabelStatic->setObjectName(QString::fromUtf8("statusLabelStatic"));
        statusLabelStatic->setGeometry(QRect(250, 100, 71, 81));
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(statusLabelStatic->sizePolicy().hasHeightForWidth());
        statusLabelStatic->setSizePolicy(sizePolicy);
        QFont font1;
        font1.setPointSize(15);
        statusLabelStatic->setFont(font1);
        statusLabel = new QLabel(centralWidget);
        statusLabel->setObjectName(QString::fromUtf8("statusLabel"));
        statusLabel->setGeometry(QRect(330, 90, 251, 100));
        QFont font2;
        font2.setPointSize(32);
        statusLabel->setFont(font2);
        statusLabel->setAlignment(Qt::AlignCenter);
        MainWindow->setCentralWidget(centralWidget);
        menuBar = new QMenuBar(MainWindow);
        menuBar->setObjectName(QString::fromUtf8("menuBar"));
        menuBar->setGeometry(QRect(0, 0, 600, 23));
        menuMain_C2 = new QMenu(menuBar);
        menuMain_C2->setObjectName(QString::fromUtf8("menuMain_C2"));
        menuHelp = new QMenu(menuBar);
        menuHelp->setObjectName(QString::fromUtf8("menuHelp"));
        MainWindow->setMenuBar(menuBar);
        mainToolBar = new QToolBar(MainWindow);
        mainToolBar->setObjectName(QString::fromUtf8("mainToolBar"));
        MainWindow->addToolBar(Qt::TopToolBarArea, mainToolBar);
        statusBar = new QStatusBar(MainWindow);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        MainWindow->setStatusBar(statusBar);

        menuBar->addAction(menuMain_C2->menuAction());
        menuBar->addAction(menuHelp->menuAction());

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "SCUTUM GUI", 0, QApplication::UnicodeUTF8));
        enableButton->setText(QApplication::translate("MainWindow", "ENABLE", 0, QApplication::UnicodeUTF8));
        disableButton->setText(QApplication::translate("MainWindow", "DISABLE", 0, QApplication::UnicodeUTF8));
        disabletempButton->setText(QApplication::translate("MainWindow", "DISABLE (temporarily)", 0, QApplication::UnicodeUTF8));
        titleLabel->setText(QApplication::translate("MainWindow", "SCUTUM Firewall GUI Controller", 0, QApplication::UnicodeUTF8));
        statusLabelStatic->setText(QApplication::translate("MainWindow", "Status: ", 0, QApplication::UnicodeUTF8));
        statusLabel->setText(QApplication::translate("MainWindow", "ENABLED", 0, QApplication::UnicodeUTF8));
        menuMain_C2->setTitle(QApplication::translate("MainWindow", "&Main C2", 0, QApplication::UnicodeUTF8));
        menuHelp->setTitle(QApplication::translate("MainWindow", "He&lp", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
